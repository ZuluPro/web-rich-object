try:
    from urllib.request import urlopen, Request
    from urllib.parse import urlparse, urljoin
except ImportError:
    from urllib2 import urlopen, Request
    from urlparse import urlparse, urljoin
import bs4

DEFAULT_USER_AGENT = 'Web Rich Object Client'


class WebRichObject(object):
    def __init__(self, url=None, html=None, headers=None, user_agent=None):
        if url is None and html is None:
            raise ValueError("You must specify a URL or HTML content")
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        if url is not None:
            response = self.urlopen(url, headers=headers)
            self.info = vars(response.info())
            self.request_headers = dict([h.strip().split(':', 1)
                                         for h in self.info['headers']])
            self.html = response.read()
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
        parsed_img_url = urlparse(url)
        parsed_base_url = urlparse(self.base_url)
        if parsed_img_url.path.startswith('/'):
            base_url = '%(scheme)s://%(hostname)s' % {
                'scheme': parsed_base_url.scheme,
                'hostname': parsed_base_url.hostname
            }
        else:
            base_url = self.base_url
        return urljoin(base_url, url)

    # Mandatory fields
    @property
    def title(self):
        if not hasattr(self, '_title'):
            self._title = None
            # If HTML
            if self.soup.find():
                # Try opengraph
                title_tag = self.soup.find('meta', property='og:title')
                if title_tag is not None:
                    self._title = title_tag.attrs['content']
                # Check with <title>
                if self._title is None:
                    title_tag = self.soup.find('title')
                    if title_tag is not None:
                        self._title = title_tag.text
            # If no title, take the URL
            if self._title is None and self.base_url is not None:
                self._title = self.base_url
        return self._title

    @property
    def type(self):
        if not hasattr(self, '_type'):
            self._type = None
            if self.info.get('maintype', 'text') not in ('text', 'text/html'):
                self._type = self.info['maintype']
            else:
                if 'facebook.com/' in self.url and '/videos/' in self.url:
                    self._type = 'video'
                if self._type is None:
                    type_tag = self.soup.find('meta', property='og:type')
                    if type_tag is not None:
                        self._type = type_tag.attrs['content']
                if self._type is None:
                    self._type = 'website'
        return self._type

    @property
    def image(self):
        if not hasattr(self, '_image'):
            self._image = None
            # If is image take its URL
            if self.info.get('maintype') == 'image':
                self._image = self.base_url
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
                if image_tag is not None:
                    self._image = image_tag.attrs['content']
            # Get first image
            if self._image is None:
                img_tag = self.soup.find('img', src=True)
                if img_tag is not None:
                        self._image = img_tag.attrs['src']
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
            url_tag = self.soup.find('meta', property='og:url')
            if url_tag is not None:
                self._url = url_tag.attrs['content']
            if self._url is None:
                self._url = self.base_url
        return self._url

    # Optional
    @property
    def generator(self):
        if not hasattr(self, '_generator'):
            self._generator = None
            generator_tag = self.soup.find('meta', attrs={'name': "generator"})
            if generator_tag is not None:
                self._generator = generator_tag.attrs['content']
        return self._generator

    @property
    def description(self):
        if not hasattr(self, '_description'):
            self._description = None
            # MediaWiki special case
            if self.generator and 'MediaWiki' in self.generator:
                description_text = self.soup.find('p').getText()
                self._description = description_text[:100]
                if len(self._description) < description_text:
                    self._description += '...'
            # from opengraph
            if self._description is None:
                description_tag = self.soup.find('meta', property='og:description')
                if description_tag is not None:
                    self._description = description_tag.attrs['content']
            # from meta description
            if self._description is None:
                description_tag = self.soup.find('meta', attrs={'name': 'description'})
                if description_tag is not None:
                    self._description = description_tag.attrs['content']
        return self._description

    @property
    def audio(self):
        if not hasattr(self, '_audio'):
            self._audio = None
            audio_tag = self.soup.find('meta', property='og:audio')
            if audio_tag:
                self._audio = audio_tag.attrs['content']
        return self._audio

    @property
    def determiner(self):
        if not hasattr(self, '_determiner'):
            self._determiner = None
            determiner_tag = self.soup.find('meta', property='og:determiner')
            if determiner_tag is not None:
                self._determiner = determiner_tag.attrs['content']
            else:
                self._determiner = 'auto'
        return self._determiner

    @property
    def locale(self):
        if not hasattr(self, '_locale'):
            self._locale = None
            # If HTML ; with open graph
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
            site_name_tag = self.soup.find('meta', property='og:site_name')
            if site_name_tag is not None:
                self._site_name = site_name_tag.attrs['content']
            if self._site_name is None:
                self._site_name = urlparse(self.base_url).hostname
        return self._site_name

    @property
    def video(self):
        if not hasattr(self, '_video'):
            self._video = None
            video_tag = self.soup.find('meta', property='og:video')
            if video_tag is not None:
                self._video = video_tag.attrs['content']
        return self._video

    @property
    def images(self):
        if not hasattr(self, '_images'):
            self._images = [
                t.attrs['content']
                for t in
                self.soup.find_all('meta', property='og:image')
            ]
        return self._images

    @property
    def author(self):
        if not hasattr(self, '_author'):
            # from opengraph og:author
            self._author = None
            # from og:author, XXX: Hack
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
            # from HTML meta author
            if self._author is None:
                meta_author_tag = self.soup.find('meta', name='author')
                if og_author_article_tag is not None:
                    self._author = meta_author_tag.attrs['content']
        return self._author

    @property
    def published_time(self):
        if not hasattr(self, '_published_time'):
            self._published_time = None
            # from og:published_time, XXX: Hack
            og_pt_tag = self.soup.find('meta', property='og:published_time')
            if og_pt_tag is not None:
                self._published_time = og_pt_tag.attrs['content']
            # from opengraph article_published_time
            if self.published_time is None:
                og_article_pt_tag = self.soup.find('meta', property='article:published_time')
                if og_article_pt_tag is not None:
                    self._published_time = og_article_pt_tag.attrs['content']
            # from html5 issued
            if self.published_time is None:
                og_issued_tag = self.soup.find('meta', name='issued')
                if og_issued_tag is not None:
                    self.published_time = og_issued_tag['content']
        return self._published_time

    @property
    def modified_time(self):
        if not hasattr(self, '_modified_time'):
            self._modified_time = None
            # from og:modified_time, XXX: Hack
            og_md_tag = self.soup.find('meta', property='og:modified_time')
            if og_md_tag is not None:
                self._modified_time = og_md_tag.attrs['content']
            # from opengraph article_modified_time
            if self.modified_time is None:
                og_article_md_tag = self.soup.find('meta', property='article:modified_time')
                if og_article_md_tag is not None:
                    self._modified_time = og_article_md_tag.attrs['content']
            # from html5 issued
            if self.modified_time is None:
                og_issued_tag = self.soup.find('meta', name='modified')
                if og_issued_tag is not None:
                    self.modified_time = og_issued_tag['content']
        return self._modified_time

    @property
    def expiration_time(self):
        if not hasattr(self, '_expiration_time'):
            self._expiration_time = None
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
            # from og:section, XXX: Hack
            og_section_tag = self.soup.find('meta', property='og:section')
            if og_section_tag is not None:
                self._expiration_time = og_section_tag.attrs['content']
            # from opengraph article:section
            if self.expiration_time is None:
                og_article_section_tag = self.soup.find('meta', property='article:section')
                if og_article_section_tag is not None:
                    self._expiration_time = og_article_section_tag.attrs['content']
        return self._section

    @property
    def tags(self):
        if not hasattr(self, '_tags'):
            self._tags = []
            # from og:tag, XXX: Hack
            og_tag_tags = self.soup.findall('meta', property='og:tag')
            for tag in og_tag_tags:
                og_tag_tags.append(tag.attrs['og:tag'])
            # from opengraph article:tags
            og_tag_tags = self.soup.findall('meta', property='article:tag')
            for tag in og_tag_tags:
                og_tag_tags.append(tag.attrs['og:tag'])
        return self._section

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
