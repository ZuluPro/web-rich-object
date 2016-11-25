import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from web_rich_object.api import (
    WebRichObject as WRO,
    DEFAULT_USER_AGENT
)


class WebRichObjectFunctionalTest(unittest.TestCase):
    def test_website(self):
        url = 'http://example.com'
        wro = WRO(url)
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
        'return_value.read.return_value': '<html><html>',
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

    def test_from_og_image(self):
        pass

    def test_from_link_tag(self):
        pass

    def test_from_favicon(self):
        pass

    def test_from_1st_image(self):
        pass

    def test_from_relative_path(self):
        pass


class WebRichObjectUrlTest(unittest.TestCase):
    def test_from_og_url(self):
        pass

    def test_default_is_base_url(self):
        pass


class WebRichObjectDescriptionTest(unittest.TestCase):
    def test_from_og_description(self):
        pass

    def test_from_meta_tag(self):
        pass

    def test_default_is_none(self):
        pass


class WebRichObjectAudioTest(unittest.TestCase):
    def test_from_og_audio(self):
        pass

    def test_default_is_none(self):
        pass


class WebRichObjectDeterminerTest(unittest.TestCase):
    def test_from_og_determiner(self):
        pass

    def test_default_is_none(self):
        pass


class WebRichObjectLocaleTest(unittest.TestCase):
    def test_from_og_locale(self):
        pass

    def test_from_lang_tag(self):
        pass

    def test_from_xml_lang_tag(self):
        pass

    def test_from_content_language_headers(self):
        pass

    def test_default_is_none(self):
        pass


class WebRichObjectLocaleAlternativeTest(unittest.TestCase):
    def test_from_og_alternative(self):
        pass

    def test_default_is_none(self):
        pass


class WebRichObjectSiteNameTest(unittest.TestCase):
    def test_from_og_site_name(self):
        pass

    def test_default_is_hostname(self):
        pass


class WebRichObjectVideoTest(unittest.TestCase):
    def test_from_og_video(self):
        pass

    def test_default_is_none(self):
        pass


class WebRichObjectImagesTest(unittest.TestCase):
    def test_from_og_images(self):
        pass

    def test_default_is_none(self):
        pass


class WebRichObjectStructImageTest(unittest.TestCase):
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
