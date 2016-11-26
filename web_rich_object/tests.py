import unittest
try:
    from unittest.mock import patch
    from urllib import URLError
except ImportError:
    from mock import patch
    from urllib2 import URLError
from web_rich_object.api import (
    WebRichObject as WRO,
    DEFAULT_USER_AGENT
)


class WebRichObjectFunctionalTest(unittest.TestCase):
    def test_website(self):
        url = 'http://example.com'
        try:
            wro = WRO(url)
        except URLError as err:
            self.skipTest("Can't test: %s" % err)
        self.assertEqual(wro.title, 'Example Domain')
        self.assertEqual(wro.base_url, url)
        self.assertEqual(wro.site_name, 'example.com')
        self.assertEqual(wro.type, 'website')
        self.assertEqual(wro.image, None)


class WebRichObjectInitTest(unittest.TestCase):
    url = 'http://example.com'

    def test_no_url_nor_html(self):
        with self.assertRaises(ValueError):
            WRO()

    @patch('web_rich_object.api.urlopen', **{
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_url(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.base_url, self.url)
        self.assertEqual(wro.info, {'headers': ''})
        self.assertEqual(wro.request_headers, {})
        self.assertTrue(mock_urlopen.called)
        # test request
        request = mock_urlopen.call_args[0][0]
        self.assertEqual(request.headers['User-agent'], DEFAULT_USER_AGENT)

    @patch('web_rich_object.api.urlopen', **{
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_url_headers(self, mock_urlopen):
        wro = WRO(self.url, headers={'Foo': 'bar'})
        self.assertTrue(mock_urlopen.called)
        # test request
        request = mock_urlopen.call_args[0][0]
        self.assertIn('Foo', request.headers)
        self.assertEqual(request.headers['Foo'], 'bar')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_url_user_agent(self, mock_urlopen):
        wro = WRO(self.url, user_agent='foo')
        self.assertTrue(mock_urlopen.called)
        # test request
        request = mock_urlopen.call_args[0][0]
        self.assertIn('User-agent', request.headers)
        self.assertEqual(request.headers['User-agent'], 'foo')

    @patch('web_rich_object.api.urlopen')
    def test_html(self, mock_urlopen):
        html = '<html></html>'
        wro = WRO(html=html)
        self.assertFalse(mock_urlopen.called)


# TODO: Make staticmethod
# @patch('web_rich_object.api.urlopen')
# class WebRichObjectUrlopenTest(unittest.TestCase):
#     def setUp(self):
#         self.wro = WRO()
# 
#     def test_func(self):
#         pass
# 
#     def test_no_ua_specified(self):
#         pass
# 
#     def test_header(self):
#         pass
# 
#     def test_user_agent(self):
#         pass


class WebRichObjectSoupTest(unittest.TestCase):
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


class WebRichObjectTitleTest(unittest.TestCase):
    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_no_title_is_url(self, mock_urlopen):
        url = 'http://example.com'
        wro = WRO(url)
        self.assertEqual(wro.title, url)

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:title" content="foo"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_title(self, mock_urlopen):
        url = 'http://example.com'
        wro = WRO(url)
        self.assertEqual(wro.title, 'foo')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><title>foo</title></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_title_tag(self, mock_urlopen):
        url = 'http://example.com'
        wro = WRO(url)
        self.assertEqual(wro.title, 'foo')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': b'bar',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_not_html(self, mock_urlopen):
        url = 'http://example.com'
        wro = WRO(url)
        self.assertEqual(wro.title, url)


class WebRichObjectTypeTest(unittest.TestCase):
    url = 'http://example.com'

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:type" content="foo"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_type(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.type, 'foo')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': b'foo',
        'return_value.info.return_value.__dict__': {'maintype': 'image',
                                                    'headers': ''},
    })
    def test_from_headers(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.type, 'image')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_unknown(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.type, 'website')


class WebRichObjectImage(unittest.TestCase):
    url = 'http://example.com'

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': b'foo',
        'return_value.info.return_value.__dict__': {'maintype': 'image',
                                                    'headers': ''},
    })
    def test_is_image_from_headers(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.image, self.url)

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:image" content="http://foo.png"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_image(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.image, 'http://foo.png')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><link rel="icon" href="/favicon.ico" type="image/x-icon"></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_favicon_shortcut_icon(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.image, 'http://example.com/favicon.ico')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><img src="/foo.png"></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_first_image(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.image, 'http://example.com/foo.png')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><img src="foo.png"></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_relative_path(self, mock_urlopen):
        wro = WRO(self.url + '/bar/')
        self.assertEqual(wro.image, 'http://example.com/bar/foo.png')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><img src="/foo.png"></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_relative_path_from_root(self, mock_urlopen):
        wro = WRO(self.url + '/bar/')
        self.assertEqual(wro.image, 'http://example.com/foo.png')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><img src="//example.com/foo.png"></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_relative_protocol(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.image, 'http://example.com/foo.png')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_default_is_none(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.image, None)


class WebRichObjectUrlTest(unittest.TestCase):
    url = 'http://example.com'

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:url" content="http://example.com/foo"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_url(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.url, 'http://example.com/foo')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_default_is_base_url(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.url, wro.base_url)


class WebRichObjectDescriptionTest(unittest.TestCase):
    url = 'http://example.com'

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:description" content="foo"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_description(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.description, 'foo')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta name="description" content="foo"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_meta_tag(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.description, 'foo')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_default_is_none(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.description, None)


class WebRichObjectAudioTest(unittest.TestCase):
    url = 'http://example.com'

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:audio" content="http://example.com/foo.mp4"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_audio(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.audio, 'http://example.com/foo.mp4')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><audio controls><source src="http://example.com/foo.mp4" type="audio/mpeg"></audio><html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_first_audio(self, mock_urlopen):
        self.skipTest("Not implemented")
        wro = WRO(self.url)
        self.assertEqual(wro.audio, 'http://example.com/foo.mp4')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><audio controls><source src="foo.mp4" type="audio/mpeg"></audio><html>',
        'return_value.read.return_value': '<html><img src="foo.png"></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_relative_path(self, mock_urlopen):
        self.skipTest("Not implemented")
        wro = WRO(self.url + '/bar/')
        self.assertEqual(wro.audio, 'http://example.com/bar/foo.mp4')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><audio controls><source src="/foo.mp4" type="audio/mpeg"></audio><html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_relative_path_from_root(self, mock_urlopen):
        self.skipTest("Not implemented")
        wro = WRO(self.url + '/bar/')
        self.assertEqual(wro.audio, 'http://example.com/foo.mp4')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><audio controls><source src="//example.com/foo.mp4" type="audio/mpeg"></audio><html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_relative_protocol(self, mock_urlopen):
        self.skipTest("Not implemented")
        wro = WRO(self.url)
        self.assertEqual(wro.audio, 'http://example.com/foo.mp4')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_default_is_none(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.audio, None)


class WebRichObjectDeterminerTest(unittest.TestCase):
    url = 'http://example.com'

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:determiner" content="foo"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_determiner(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.determiner, 'foo')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_default_is_auto(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.determiner, 'auto')


class WebRichObjectLocaleTest(unittest.TestCase):
    url = 'http://example.com'

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:locale" content="PT"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_locale(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.locale, 'PT')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html lang="PT"></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_lang_tag(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.locale, 'PT')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html xml:lang="PT"></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_xml_lang_tag(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.locale, 'PT')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ['Content-Language:PT']},
    })
    def test_from_content_language_headers(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.locale, 'PT')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_default_is_none(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.locale, None)


class WebRichObjectLocaleAlternativeTest(unittest.TestCase):
    url = 'http://example.com'

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:locale_alternative" content="PT"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_alternative(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.locale_alternative, ['PT'])

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_default_is_empty(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.locale_alternative, [])


class WebRichObjectSiteNameTest(unittest.TestCase):
    url = 'http://example.com'

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:site_name" content="Foo"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_site_name(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.site_name, 'Foo')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_default_is_hostname(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.site_name, 'example.com')


class WebRichObjectVideoTest(unittest.TestCase):
    url = 'http://example.com'

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:video" content="foo.mp4"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_video(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.video, 'foo.mp4')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:video" content="foo.mp4"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_relative_path(self, mock_urlopen):
        self.skipTest("Not implemented")
        wro = WRO(self.url + '/bar/')
        self.assertEqual(wro.audio, 'http://example.com/bar/foo.mp4')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:video" content="/foo.mp4"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_relative_path_from_root(self, mock_urlopen):
        self.skipTest("Not implemented")
        wro = WRO(self.url + '/bar/')
        self.assertEqual(wro.audio, 'http://example.com/foo.mp4')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:video" content="//example.com/foo.mp4"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_relative_protocol(self, mock_urlopen):
        self.skipTest("Not implemented")
        wro = WRO(self.url)
        self.assertEqual(wro.audio, 'http://example.com/foo.mp4')

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_default_is_none(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.video, None)


class WebRichObjectImagesTest(unittest.TestCase):
    url = 'http://example.com'

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html><meta property="og:image" content="/foo.mp4"/></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_from_og_images(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.images, ['/foo.mp4'])

    @patch('web_rich_object.api.urlopen', **{
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': {'headers': ''},
    })
    def test_default_is_empty(self, mock_urlopen):
        wro = WRO(self.url)
        self.assertEqual(wro.images, [])


class WebRichObjectStructImageTest(unittest.TestCase):
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


class WebRichObjectStructVideoTest(unittest.TestCase):
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


class WebRichObjectStructAudioTest(unittest.TestCase):
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
