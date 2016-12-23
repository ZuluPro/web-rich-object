import os
import json
from io import BytesIO
try:
    from urllib.request import urlopen, Request
    from urllib.parse import urlparse, urljoin
    from urllib import unquote
except ImportError:
    from urllib2 import urlopen, Request, unquote
    from urlparse import urlparse, urljoin

import bs4
import chardet
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

from web_rich_object import utils

DEFAULT_USER_AGENT = os.environ.get('WRO_USER_AGENT', 'Web Rich Object Client')
DOWNLOAD_MAX_SIZE = int(os.environ.get('WRO_DOWNLOAD_MAX_SIZE', 10*10**6))


class WebRichObject(object):
    def __init__(self, url=None, html=None, headers=None, user_agent=None):
        if url is None and html is None:
            raise ValueError("You must specify a URL or HTML content")
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        if url is not None:
            response = self.urlopen(url, headers=headers)
            self.info = vars(response.info())
            self.request_headers = dict([
                [i.strip() for i in h.split(':', 1)]
                for h in self.info['headers']
            ])
            self.html = response.read(DOWNLOAD_MAX_SIZE)
        else:
            self.info = {}
            self.request_headers = {}
            self.html = html
        self.base_url = url

    # TODO: Make staticmethod
    def urlopen(self, url, headers):
        headers = headers or {}
        if not headers.get('User-Agent'):
            headers['User-Agent'] = self.user_agent
        req = Request(url.encode('utf-8'), headers=headers)
        return urlopen(req)

    @property
    def soup(self):
        if not hasattr(self, '_soup'):
            self._soup = bs4.BeautifulSoup(self.html, 'html.parser')
        return self._soup

    def _format_url(self, url):
        parsed_url = urlparse(url)
        parsed_base_url = urlparse(self.base_url)
        if parsed_url.path.startswith('/'):
            base_url = '%(scheme)s://%(hostname)s' % {
                'scheme': parsed_base_url.scheme,
                'hostname': parsed_base_url.hostname
            }
        else:
            base_url = self.base_url
        return urljoin(base_url, url)

    @property
    def pdf_info(self):
        if not hasattr(self, '_pdf_info'):
            try:
                fp = BytesIO(self.html)
                parser = PDFParser(fp)
                doc = PDFDocument(parser)
                self._pdf_info = doc.info
            except:
                self._pdf_info = None
        return self._pdf_info

    @property
    def contextly_info(self):
        if not hasattr(self, '_contextly_info'):
            self._contextly_info = {}
            contextly_tag = self.soup.find('meta', attrs={'name': 'contextly-page'})
            if contextly_tag is not None and contextly_tag.attrs.get('content'):
                self._contextly_info = json.loads(contextly_tag.attrs['content'])
                if self._contextly_info.get('pub_date'):
                    self._contextly_info['pub_date'] = utils.parse_contextly_time(self._contextly_info['pub_date'])
                if self._contextly_info.get('mod_date'):
                    self._contextly_info['mod_date'] = utils.parse_contextly_time(self._contextly_info['mod_date'])
        return self._contextly_info

    def _valid_string(self, value):
        if not value:
            return None
        if value.startswith('{{') and value.endswith('}}'):
            return None
        return value.strip()

    # Mandatory fields
    @property
    def title(self):
        if not hasattr(self, '_title'):
            self._title = None
            # PDF
            if self.subtype == 'pdf' and self.pdf_info:
                raw_title = self.pdf_info[0].get('Title', None)
                if raw_title:
                    charset = chardet.detect(raw_title)['encoding']
                    if charset not in ('ascii', 'utf8'):
                        raw_title = raw_title[2:]
                    self._title = raw_title.decode(charset, 'ignore')
            # HTML
            elif self.subtype == 'html' and self.soup.find():
                # Try opengraph
                title_tag = self.soup.find('meta', property='og:title')
                if title_tag is not None:
                    title = self._valid_string(title_tag.attrs.get('content'))
                    if title:
                        self._title = title_tag.attrs['content']
                # Check with <title>
                if self._title is None:
                    title_tag = self.soup.find('title')
                    if title_tag is not None:
                        self._title = self._valid_string(title_tag.text)
                # Get from contextly-data
                if (self._title is None and self.contextly_info and
                        self.contextly_info.get('title')):
                    self._title = self._valid_string(self.contextly_info['title'])
            # From file name
            if not self._title and not self.subtype == 'html':
                parsed_url = urlparse(self.base_url)
                filename = parsed_url.path.split('/')[-1:]
                if filename:
                    self._title = unquote(filename[0])
            # If no title, take the URL
            if not self._title and self.site_name is not None:
                self._title = self.site_name
        return self._title

    @property
    def type(self):
        if not hasattr(self, '_type'):
            self._type = None
            if self.info.get('maintype', 'text') not in ('text', 'text/html'):
                self._type = self.info['maintype']
            # Guess embed video link
            elif 'facebook.com/' in self.url and '/videos/' in self.url:
                self._type = 'video'
            elif self.info.get('maintype') == 'text':
                og_type_tag = self.soup.find('meta', property='og:type')
                if og_type_tag is not None:
                    type_ = og_type_tag.attrs['content']
                    type_ = self._valid_string(type_)
                    if type_ is not None:
                        # Remove  prefix
                        content = type_.split(':')[-1]
                        self._type = content
                # Default for text is website
                if self._type is None:
                    self._type = 'website'
                # Get from contextly-data
                if (self._type is None and self.contextly_info and
                        self.contextly_info.get('type')):
                    type_ = self._valid_string(self.contextly_info['type'])
                    self._type = self.contextly_info['type']
            else:
                self._type = self.info.get('type')
            if self._type:
                self._type = self._type.lower()
        return self._type

    @property
    def image(self):
        if not hasattr(self, '_image'):
            self._image = None
            # If is image take its URL
            if self.info.get('maintype') == 'image':
                self._image = self.base_url
            # HTML
            elif self.subtype == 'html' and self.soup.find():
                # MediaWiki
                if self._image is None and self.generator and 'MediaWiki' in self.generator:
                    thumb_tag = self.soup.find('div', attrs={'class': 'thumbinner'})
                    if thumb_tag is not None:
                        img_tag = thumb_tag.find('img')
                        if img_tag is not None:
                            self._image = img_tag.attrs['src']
                # Get from opengraph
                if self._image is None:
                    image_tag = self.soup.find('meta', property='og:image')
                    if image_tag is not None and image_tag.attrs.get('content'):
                        image = self._valid_string(image_tag.attrs['content'])
                        self._image = image
                # Get from contextly-data
                if (self._image is None and self.contextly_info and
                        self.contextly_info.get('image')):
                    image = self._valid_string(self.contextly_info['image'])
                    self._image = image
                # Get biggest image
                if self._image is None:
                    image_urls = [self._format_url(i.attrs['src'])
                                  for i in self.soup.find_all('img')
                                  if 'src' in i.attrs]
                    self._image = utils.get_biggest_image(image_urls)
                # Get from favicon
                if self._image is None:
                    favicon_tag = self.soup.find('link',
                                                 property="shortcut icon")
                    if favicon_tag is not None:
                        self._image = favicon_tag.attrs['href']
                # 2nd try for favicon
                if self._image is None:
                    favicon_tag = self.soup.find('link', rel="icon")
                    if favicon_tag is not None:
                        self._image = favicon_tag.attrs['href']
            # Format URL
            if self._image is not None and not self._image.startswith('http'):
                self._image = self._format_url(self._image)

        return self._image

    @property
    def url(self):
        if not hasattr(self, '_url'):
            self._url = None
            if self.subtype == 'html' and self.soup.find():
                url_tag = self.soup.find('meta', property='og:url')
                if url_tag is not None and url_tag.attrs.get('content'):
                    self._url = self._valid_string(url_tag.attrs['content'])
                # Get from contextly-data
                if (self._url is None and self.contextly_info and
                        self.contextly_info.get('url')):
                    self._url = self._valid_string(self.contextly_info['url'])
            if self._url is None:
                self._url = self.base_url
        return self._url

    # Optional
    @property
    def subtype(self):
        if not hasattr(self, '_subtype'):
            self._subtype = self.info['subtype']
        return self._subtype

    @property
    def generator(self):
        if not hasattr(self, '_generator'):
            self._generator = None
            # PDF
            if self.subtype == 'pdf' and self.pdf_info:
                creator = self.pdf_info[0].get('Creator', None)
                if creator:
                    self._generator = creator
                else:
                    producer = self.pdf_info[0].get('Producer', None)
                    if producer:
                        self._generator = producer
            # HTML
            elif self.subtype == 'html' and self.soup.find():
                generator_tag = self.soup.find('meta', attrs={'name': "generator"})
                if generator_tag is not None:
                    self._generator = generator_tag.attrs['content']
        return self._generator

    @property
    def description(self):
        if not hasattr(self, '_description'):
            self._description = None
            # PDF
            if self.subtype == 'pdf' and self.pdf_info:
                self._description = self.pdf_info[0].get('Subject', None)
            # HTML
            elif self.subtype == 'html' and self.soup.find():
                # from opengraph
                if self._description is None:
                    desc_tag = self.soup.find('meta', property='og:description')
                    if desc_tag is not None and desc_tag.attrs.get('content'):
                        desc = self._valid_string(desc_tag.attrs['content'])
                        self._description = desc
                # from meta description
                if self._description is None:
                    desc_tag = self.soup.find('meta', attrs={'name': 'description'})
                    if desc_tag is not None and desc_tag.attrs.get('content'):
                        desc = self._valid_string(desc_tag.attrs['content'])
                        self._description = desc
                # Get first p
                if self._description is None:
                    for p_tag in self.soup.find_all('p'):
                        description_text = p_tag.getText()
                        if not description_text.strip() or len(description_text) < 20:
                            continue
                        self._description = description_text[:100]
                        if len(self._description) < description_text:
                            self._description += '...'
                        break
        return self._description

    @property
    def audio(self):
        if not hasattr(self, '_audio'):
            self._audio = None
            # HTML
            if self.subtype == 'html' and self.soup.find():
                audio_tag = self.soup.find('meta', property='og:audio')
                if audio_tag:
                    self._audio = audio_tag.attrs['content']
        return self._audio

    @property
    def determiner(self):
        if not hasattr(self, '_determiner'):
            self._determiner = None
            # HTML
            if self.subtype == 'html' and self.soup.find():
                determiner_tag = self.soup.find('meta', property='og:determiner')
                if determiner_tag is not None:
                    self._determiner = determiner_tag.attrs['content']
        if self._determiner is None:
            self._determiner = 'auto'
        return self._determiner

    @property
    def locale(self):
        if not hasattr(self, '_locale'):
            self._locale = None
            # HTML
            if self.subtype == 'html' and self.soup.find():
                # from open graph
                locale_tag = self.soup.find('meta', property='og:locale')
                if locale_tag is not None:
                    self._locale = locale_tag.attrs['content']
                # Or get with HTML tag
                if self._locale is None:
                    html_tag = self.soup.find('html')
                    if html_tag is not None:
                        self._locale = html_tag.attrs.get('lang')
                        if self._locale is None:
                            self._locale = html_tag.attrs.get('xml:lang')
                # Get from response header
                if self._locale is None and self.request_headers:
                    self._locale = self.request_headers.get('Content-Language')
            if self._locale is not None:
                self._locale = self._locale.upper()
        return self._locale

    @property
    def locale_alternative(self):
        if not hasattr(self, '_locale_alternative'):
            self._locale_alternative = [
                t.attrs['content']
                for t in
                self.soup.find_all('meta', property='og:locale_alternative')
            ]
        return self._locale_alternative

    @property
    def site_name(self):
        if not hasattr(self, '_site_name'):
            self._site_name = None
            # HTML
            if self.subtype == 'html' and self.soup.find():
                site_name_tag = self.soup.find('meta', property='og:site_name')
                if site_name_tag is not None:
                    self._site_name = site_name_tag.attrs['content']
            # If unfound get from URL
            if self._site_name is None:
                self._site_name = urlparse(self.base_url).hostname
        return self._site_name

    @property
    def video(self):
        if not hasattr(self, '_video'):
            self._video = None
            if self.subtype == 'html' and self.soup.find():
                # From open graph
                og_video_tag = self.soup.find('meta', property='og:video')
                if og_video_tag is not None:
                    self._video = og_video_tag.attrs['content']
                # From open graph video url
                if self._video is None:
                    og_video_tag = self.soup.find('meta', property='og:video:url')
                    if og_video_tag is not None:
                        self._video = og_video_tag.attrs['content']
                # From open graph video secure url
                if self._video is None:
                    og_video_tag = self.soup.find('meta', property='og:video:secure_url')
                    if og_video_tag is not None:
                        self._video = og_video_tag.attrs['content']
                # From HTML5 video_tag
                video_tag = self.soup.find('video')
                if video_tag is not None:
                    source_tag = video_tag.find('source')
                    if source_tag is not None:
                        self._video = source_tag.attrs['src']
            elif self.info['maintype'] == 'video':
                self._video = self.base_url
            # Format URL
            if self._video is not None and not self._video.startswith('http'):
                self._video = self._format_url(self._video)
        return self._video

    @property
    def images(self):
        if not hasattr(self, '_images'):
            self._images = []
            if self.subtype == 'html' and self.soup.find():
                self._images = [
                    t.attrs['content']
                    for t in
                    self.soup.find_all('meta', property='og:image')
                ]
        return self._images

    @property
    def author(self):
        if not hasattr(self, '_author'):
            self._author = None
            # PDF
            if self.subtype == 'pdf' and self.pdf_info:
                self._author = self.pdf_info[0].get('Author', None)
            # HTML
            elif self.subtype == 'html' and self.soup.find():
                # from og:author
                og_author_tag = self.soup.find('meta', property='og:author')
                if og_author_tag is not None:
                    self._author = og_author_tag.attrs['content']
                # from opengraph article:author
                if self._author is None:
                    og_author_article_tag = self.soup.find('meta', property='article:author')
                    if og_author_article_tag is not None:
                        self._author = og_author_article_tag.attrs['content']
                # from opengraph book:author
                if self._author is None:
                    og_author_article_tag = self.soup.find('meta', property='book:author')
                    if og_author_article_tag is not None:
                        self._author = og_author_article_tag.attrs['content']
                # Get from contextly-data
                if self._author is None and self.contextly_info:
                    if self.contextly_info.get('author_display_name'):
                        self._author = self.contextly_info['author_display_name']
                    elif self.contextly_info.get('author_name'):
                        self._author = self.contextly_info['author_name']
                # from HTML meta author
                if self._author is None:
                    meta_author_tag = self.soup.find('meta', attrs={'name': 'author'})
                    if og_author_article_tag is not None:
                        self._author = meta_author_tag.attrs['content']
        return self._author

    @property
    def created_time(self):
        if not hasattr(self, '_created_time'):
            self._created_time = None
            # PDF
            if self.subtype == 'pdf' and self.pdf_info:
                date_str = self.pdf_info[0].get('CreationDate', None)
                if date_str:
                    self._created_time = utils.parse_pdf_time(date_str)
        return self._created_time

    @property
    def published_time(self):
        if not hasattr(self, '_published_time'):
            self._published_time = None
            # HTML
            if self.subtype == 'html' and self.soup.find():
                # from og:published_time, XXX: Hack
                og_pt_tag = self.soup.find('meta', property='og:published_time')
                if og_pt_tag is not None:
                    date_str = og_pt_tag.attrs['content']
                    self._published_time = utils.parse_opengraph_time(date_str)
                # from opengraph article_published_time
                if self.published_time is None:
                    og_article_pt_tag = self.soup.find('meta', property='article:published_time')
                    if og_article_pt_tag is not None:
                        date_str = og_article_pt_tag.attrs['content']
                        self._published_time = utils.parse_opengraph_time(date_str)
                # Get from contextly-data
                if (self._published_time is None and self.contextly_info and
                        self.contextly_info.get('pub_date')):
                    self._published_time = self.contextly_info['pub_date']
                # from html5 issued
                if self.published_time is None:
                    issued_tag = self.soup.find('meta', attrs={'name': 'issued'})
                    if issued_tag is not None:
                        self.published_time = issued_tag['content']
        return self._published_time

    @property
    def modified_time(self):
        if not hasattr(self, '_modified_time'):
            self._modified_time = None
            # PDF
            if self.subtype == 'pdf' and self.pdf_info:
                date_str = self.pdf_info[0].get('ModDate', None)
                if date_str:
                    self._modified_time = utils.parse_pdf_time(date_str)
            # HTML
            elif self.subtype == 'html' and self.soup.find():
                # from og:modified_time, XXX: Hack
                og_md_tag = self.soup.find('meta', property='og:modified_time')
                if og_md_tag is not None:
                    date_str = og_md_tag.attrs['content']
                    self._modified_time = utils.parse_opengraph_time(date_str)
                # from opengraph article_modified_time
                if self.modified_time is None:
                    og_article_md_tag = self.soup.find('meta', property='article:modified_time')
                    if og_article_md_tag is not None:
                        date_str = og_article_md_tag.attrs['content']
                        self._modified_time = utils.parse_opengraph_time(date_str)
                # Get from contextly-data
                if (self._modified_time is None and self.contextly_info and
                        self.contextly_info.get('mod_date')):
                    self._modified_time = self.contextly_info['mod_date']
                # from html5 issued
                if self.modified_time is None:
                    issued_tag = self.soup.find('meta', attrs={'name': 'modified'})
                    if issued_tag is not None:
                        self.modified_time = issued_tag['content']
        return self._modified_time

    @property
    def expiration_time(self):
        if not hasattr(self, '_expiration_time'):
            self._expiration_time = None
            # HTML
            if self.subtype == 'html' and self.soup.find():
                # from og:expiration_time, XXX: Hack
                og_md_tag = self.soup.find('meta', property='og:expiration_time')
                if og_md_tag is not None:
                    self._expiration_time = og_md_tag.attrs['content']
                # from opengraph article_expiration_time
                if self.expiration_time is None:
                    og_article_md_tag = self.soup.find('meta', property='article:expiration_time')
                    if og_article_md_tag is not None:
                        self._expiration_time = og_article_md_tag.attrs['content']
        return self._expiration_time

    @property
    def section(self):
        if not hasattr(self, '_section'):
            self._section = None
            # HTML
            if self.subtype == 'html' and self.soup.find():
                # from og:section, XXX: Hack
                og_section_tag = self.soup.find('meta', property='og:section')
                if og_section_tag is not None:
                    self._expiration_time = og_section_tag.attrs['content']
                # from opengraph article:section
                if self.expiration_time is None:
                    og_article_section_tag = self.soup.find('meta', property='article:section')
                    if og_article_section_tag is not None:
                        self._expiration_time = og_article_section_tag.attrs['content']
                # Get from contextly-data
                if (self._section is None and self.contextly_info and
                        self.contextly_info.get('categories')):
                    self._section = self.contextly_info['categories'][0]
        return self._section

    category = section

    @property
    def tags(self):
        if not hasattr(self, '_tags'):
            self._tags = []
            # PDF
            if self.subtype == 'pdf' and self.pdf_info:
                keywords = self.pdf_info[0].get('Keywords', '')
                self._tags.extend(keywords.split())
            # HTML
            elif self.subtype == 'html' and self.soup.find():
                # from og:tag, XXX: Hack
                og_tag_tags = self.soup.find_all('meta', property='og:tag')
                for tag in og_tag_tags:
                    self._tags.append(tag.attrs['content'])
                # from opengraph article:tags
                article_tag_tags = self.soup.find_all('meta', property='article:tag')
                for tag in article_tag_tags:
                    self._tags.append(tag.attrs['content'])
                # from opengraph article:tags
                video_tag_tags = self.soup.find_all('meta', property='video:tag')
                for tag in video_tag_tags:
                    self._tags.append(tag.attrs['content'])
                # Get from contextly-data
                if (not self._tags and self.contextly_info and
                        self.contextly_info.get('tags')):
                    self._tags = self.contextly_info['tags']
        return self._tags

    @property
    def struct_image(self):
        if not hasattr(self, '_struct_image'):
            _image = self.soup.find('meta', property='og:image')
            self._struct_image = {}
            if _image is not None:
                self._struct_image = {
                    'url': _image.attrs['content'],
                }
                next_img_metas = _image.find_next_siblings('meta',
                                                           property=True)
                for img_meta in next_img_metas:
                    if img_meta.attrs['property'] == 'og:image':
                        break
                    elif img_meta.attrs['property'] == 'og:image:width':
                        self._struct_image['width'] = img_meta.attrs['content']
                    elif img_meta.attrs['property'] == 'og:image:height':
                        self._struct_image['height'] = img_meta.attrs['content']
                    elif img_meta.attrs['property'] == 'og:image:type':
                        self._struct_image['type'] = img_meta.attrs['content']
                    elif img_meta.attrs['property'] == 'og:image:secure_url':
                        self._struct_image['secure_url'] = img_meta.attrs['content']
        return self._struct_image

    @property
    def struct_video(self):
        if not hasattr(self, '_struct_video'):
            _video = self.soup.find('meta', property='og:video')
            self._struct_video = {}
            if _video is not None:
                self._struct_video = {
                    'url': _video.attrs['content'],
                }
                next_vid_metas = _video.find_next_siblings('meta',
                                                           property=True)
                for vid_meta in next_vid_metas:
                    if vid_meta.attrs['property'] == 'og:video':
                        break
                    elif vid_meta.attrs['property'] == 'og:video:width':
                        self._struct_video['width'] = vid_meta.attrs['content']
                    elif vid_meta.attrs['property'] == 'og:video:height':
                        self._struct_video['height'] = vid_meta.attrs['content']
                    elif vid_meta.attrs['property'] == 'og:video:type':
                        self._struct_video['type'] = vid_meta.attrs['content']
                    elif vid_meta.attrs['property'] == 'og:video:secure_url':
                        self._struct_video['secure_url'] = vid_meta.attrs['content']
        return self._struct_video

    @property
    def struct_audio(self):
        if not hasattr(self, '_struct_audio'):
            _audio = self.soup.find('meta', property='og:audio')
            self._struct_audio = {}
            if _audio is not None:
                self._struct_audio = {
                    'url': _audio.attrs['content'],
                }
                next_aud_metas = _audio.find_next_siblings('meta',
                                                           property=True)
                for aud_meta in next_aud_metas:
                    if aud_meta.attrs['property'] == 'og:audio':
                        break
                    elif aud_meta.attrs['property'] == 'og:audio:type':
                        self._struct_audio['type'] = aud_meta.attrs['content']
                    elif aud_meta.attrs['property'] == 'og:audio:secure_url':
                        self._struct_audio['secure_url'] = aud_meta.attrs['content']
        return self._struct_audio

    @property
    def obj_music_song(self):
        if not hasattr(self, '_obj_music_song'):
            self._obj_music_song = {}
            keys = ('duration', 'album', 'album:disc', 'album:track',
                    'musician')
            for key in keys:
                key_tag = self.soup.find('meta', property='music:' + key)
                if key_tag is not None:
                    self._music_song[key.replace(':', '')] = key_tag.attrs['content']
            self._obj_music_song = {} or None
        return self._obj_music_song

    @property
    def obj_music_album(self):
        if not hasattr(self, '_obj_music_album'):
            self._music_album = {}
            keys = ('song', 'song:disc', 'song:track', 'release_date',
                    'musician')
            for key in keys:
                key_tag = self.soup.find('meta', property='music:' + key)
                if key_tag is not None:
                    self._music_album[key.replace(':', '')] = key_tag.attrs['content']
            self._obj_music_album = {} or None
        return self._obj_music_album

    @property
    def obj_music_playlist(self):
        if not hasattr(self, '_obj_music_playlist'):
            self._obj_music_playlist = {}
            keys = ('song', 'song:disc', 'song:track', 'creator')
            for key in keys:
                key_tag = self.soup.find('meta', property='music:' + key)
                if key_tag is not None:
                    self._obj_music_playlist[key.replace(':', '')] = key_tag.attrs['content']
            self._obj_music_playlist = {} or None
        return self._obj_music_playlist

    @property
    def obj_music_radio_station(self):
        if not hasattr(self, '_obj_radio_station'):
            creator = self.soup.find('meta', property='music:creator')
            if creator is None:
                self._music_radio_station = None
            else:
                self._obj_music_radio_station = creator.attrs['content']
        return self._obj_music_radio_station

    @property
    def obj_video_movie(self):
        if not hasattr(self, '_obj_video_movie'):
            self._obj_video_movie = {}
            keys = ('song', 'song:disc', 'song:track', 'creator')
            for key in keys:
                key_tag = self.soup.find('meta', property='video:' + key)
                if key_tag is not None:
                    self._obj_video_movie[key.replace(':', '')] = key_tag.attrs['content']
            self._obj_video_movie = {} or None
        return self._obj_video_movie

    @property
    def obj_article(self):
        if not hasattr(self, '_obj_article'):
            self._obj_article = {}

            keys = ('published_time', 'modified_time', 'expiration_time',
                    'section')
            for key in keys:
                key_tag = self.soup.find('meta', property='article:' + key)
                if key_tag is not None:
                    self._obj_article[key.replace(':', '')] = key_tag.attrs['content']

            array_keys = ('author', 'tag')
            for key in array_keys:
                key_tags = self.soup.find_all('meta', property='article:' + key)
                for key_tag in key_tags:
                    _key = key.replace(':', '')
                    if _key not in self._obj_article:
                        self._obj_article[_key] = []
                    self._obj_article[_key] = key_tag.attrs['content']

            self._obj_article = {} or None
        return self._obj_article

    @property
    def obj_book(self):
        if not hasattr(self, '_obj_book'):
            self._obj_book = {}

            keys = ('isbn', 'release_date')
            for key in keys:
                key_tag = self.soup.find('meta', property='book:' + key)
                if key_tag is not None:
                    self._obj_book[key.replace(':', '')] = key_tag.attrs['content']

            array_keys = ('author', 'tag')
            for key in array_keys:
                key_tags = self.soup.find_all('meta', property='book:' + key)
                for key_tag in key_tags:
                    _key = key.replace(':', '')
                    if _key not in self._obj_book:
                        self._obj_book[_key] = []
                    self._obj_book[_key].append(key_tag.attrs['content'])

            self._obj_book = self._obj_book or None
        return self._obj_book

    @property
    def obj_profile(self):
        if not hasattr(self, '_obj_profile'):
            self._obj_profile = {}

            keys = ('first_name', 'last_name', 'username', 'gender')
            for key in keys:
                key_tag = self.soup.find('meta', property='profile:' + key)
                if key_tag is not None:
                    self._obj_profile[key.replace(':', '')] = key_tag.attrs['content']

            self._obj_profile = self._obj_profile or None
        return self._obj_profile
