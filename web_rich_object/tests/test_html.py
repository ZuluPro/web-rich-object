import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from web_rich_object.tests import utils
from web_rich_object.api import WebRichObject as WRO


class WroSoupTest(utils.BaseWebRichObjectTestCase):
    def test_html(self):
        html = '<html></html>'
        wro = WRO(html=html)
        self.assertEqual(str(wro.soup), html)
        self.assertIsNotNone(wro.soup.find('html'))
        wro.soup

    def test_not_html(self):
        not_html = b'Foo'
        wro = WRO(html=not_html)
        self.assertFalse(wro.soup.is_xml)


class HtmlTitleTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_title(self):
        wro = WRO(self.url)
        self.assertEqual(wro.title, 'foo')
    test_from_og_title.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:title" content="foo"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_title_tag(self):
        url = 'http://example.com'
        wro = WRO(url)
        self.assertEqual(wro.title, 'foo')
    test_from_title_tag.mock_attrs = {
        'return_value.read.return_value': '<html><title>foo</title></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class HtmlTypeTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_type(self):
        wro = WRO(self.url)
        self.assertEqual(wro.type, 'foo')
    test_from_og_type.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:type" content="foo"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_default_is_website(self):
        wro = WRO(self.url)
        self.assertEqual(wro.type, 'website')
    test_default_is_website.mock_attrs = {
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class HtmlImageTest(utils.BaseWebRichObjectTestCase):
    url = 'http://example.com'

    def test_from_og_image(self):
        wro = WRO(self.url)
        self.assertEqual(wro.image, 'http://foo.png')
    test_from_og_image.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:image" content="http://foo.png"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_favicon_shortcut_icon(self):
        wro = WRO(self.url)
        self.assertEqual(wro.image, 'http://example.com/favicon.ico')
    test_from_favicon_shortcut_icon.mock_attrs = {
        'return_value.read.return_value': '<html><link rel="icon" href="/favicon.ico" type="image/x-icon"></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_biggest_image(self):
        wro = WRO(self.url)
        with patch('web_rich_object.api.utils.get_biggest_image') as mock:
            mock.return_value = 'http://example.com/foo.png'
            self.assertEqual(wro.image, 'http://example.com/foo.png')
            self.assertTrue(mock.called)
    test_from_biggest_image.mock_attrs = {
        'return_value.read.return_value': '<html><img src="/foo.png"></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class HtmlUrlTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_url(self):
        wro = WRO(self.url)
        self.assertEqual(wro.url, 'http://example.com/foo')
    test_from_og_url.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:url" content="http://example.com/foo"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class HtmlDescriptionTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_description(self):
        wro = WRO(self.url)
        self.assertEqual(wro.description, 'foo')
    test_from_og_description.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:description" content="foo"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_meta_decription(self):
        wro = WRO(self.url)
        self.assertEqual(wro.description, 'foo')
    test_from_meta_decription.mock_attrs = {
        'return_value.read.return_value': '<html><meta name="description" content="foo"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class HtmlAudioTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_audio(self):
        wro = WRO(self.url)
        self.assertEqual(wro.audio, 'http://example.com/foo.mp4')
    test_from_og_audio.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:audio" content="http://example.com/foo.mp4"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_first_audio(self):
        self.skipTest("Not implemented")
        wro = WRO(self.url)
        self.assertEqual(wro.audio, 'http://example.com/foo.mp4')
    test_from_first_audio.mock_attrs = {
        'return_value.read.return_value': '<html><audio controls><source src="http://example.com/foo.mp4" type="audio/mpeg"></audio><html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class HtmlDeterminerTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_determiner(self):
        wro = WRO(self.url)
        self.assertEqual(wro.determiner, 'foo')
    test_from_og_determiner.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:determiner" content="foo"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class HtmlLocaleTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_locale(self):
        wro = WRO(self.url)
        self.assertEqual(wro.locale, 'RU')
    test_from_og_locale.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:locale" content="RU"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_html_lang(self):
        wro = WRO(self.url)
        self.assertEqual(wro.locale, 'FR')
    test_from_html_lang.mock_attrs = {
        'return_value.read.return_value': '<html lang="FR"></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_html_xml_lang_tag(self):
        wro = WRO(self.url)
        self.assertEqual(wro.locale, 'ES')
    test_from_html_xml_lang_tag.mock_attrs = {
        'return_value.read.return_value': '<html xml:lang="ES"></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_content_language_headers(self):
        wro = WRO(self.url)
        self.assertEqual(wro.locale, 'PT')
    test_from_content_language_headers.mock_attrs = {
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class HtmlLocaleAlternativeTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_alternative(self):
        wro = WRO(self.url)
        self.assertEqual(wro.locale_alternative, ['PT'])
    test_from_og_alternative.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:locale_alternative" content="PT"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WebRichObjectSiteNameTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_site_name(self):
        wro = WRO(self.url)
        self.assertEqual(wro.site_name, 'Foo')
    test_from_og_site_name.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:site_name" content="Foo"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WebRichObjectVideoTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_video(self):
        wro = WRO(self.url)
        self.assertEqual(wro.video, 'http://example.com/foo.mp4')
    test_from_og_video.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:video" content="foo.mp4"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_og_video_url(self):
        wro = WRO(self.url)
        self.assertEqual(wro.video, 'http://example.com/foo.mp4')
    test_from_og_video_url.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:video:url" content="foo.mp4"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_og_video_secure_url(self):
        wro = WRO(self.url)
        self.assertEqual(wro.video, 'http://example.com/foo.mp4')
    test_from_og_video_secure_url.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:video:secure_url" content="foo.mp4"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_html5_tag(self):
        wro = WRO(self.url)
        self.assertEqual(wro.video, 'http://example.com/foo.mp4')
    test_from_html5_tag.mock_attrs = {
        'return_value.read.return_value': '<html><video><source src="foo.mp4"></source></video></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WebRichObjectVideoWidthTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_video_width(self):
        wro = WRO(self.url)
        self.assertEqual(wro.video_width, '1280')
    test_from_og_video_width.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:video:width" content="1280"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WebRichObjectVideoHeightTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_video_height(self):
        wro = WRO(self.url)
        self.assertEqual(wro.video_height, '720')
    test_from_og_video_height.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:video:height" content="720"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


VIDEO_INFO = """<html>
<meta property="og:video" content="foo.mp4"/>
<meta property="og:video:width" content="1280"/>
<meta property="og:video:height" content="720"/>
</html>"""


class WebRichObjectVideoInfoTest(utils.BaseWebRichObjectTestCase):
    def test_property(self):
        wro = WRO(self.url)
        video_info = {
            'url': 'http://example.com/foo.mp4',
            'width': '1280',
            'height': '720'
        }
        self.assertEqual(wro.video_info, video_info)
    test_property.mock_attrs = {
        'return_value.read.return_value': VIDEO_INFO,
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WebRichObjectImagesTest(utils.BaseWebRichObjectTestCase):
    def test_from_og_images(self):
        wro = WRO(self.url)
        self.assertEqual(wro.images, ['/foo.png'])
    test_from_og_images.mock_attrs = {
        'return_value.read.return_value': '<html><meta property="og:image" content="/foo.png"/></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WebRichObjectStructImageTest(utils.BaseWebRichObjectTestCase):
    def setUp(self):
        self.skipTest('In progress')

    def test_url(self):
        pass

    def test_width(self):
        pass

    def test_height(self):
        pass

    def test_type(self):
        pass

    def test_secure_url(self):
        pass

    def test_default_is_empty(self):
        pass


class WebRichObjectStructVideoTest(utils.BaseWebRichObjectTestCase):
    def setUp(self):
        self.skipTest('In progress')

    def test_url(self):
        pass

    def test_width(self):
        pass

    def test_height(self):
        pass

    def test_type(self):
        pass

    def test_secure_url(self):
        pass

    def test_default_is_empty(self):
        pass


class WebRichObjectStructAudioTest(utils.BaseWebRichObjectTestCase):
    def setUp(self):
        self.skipTest('In progress')

    def test_url(self):
        pass

    def test_type(self):
        pass

    def test_secure_url(self):
        pass

    def test_default_is_empty(self):
        pass


if __name__ == '__main__':
    unittest.main()
