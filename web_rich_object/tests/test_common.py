import unittest
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from web_rich_object.tests import utils
from web_rich_object.api import WebRichObject as WRO, DEFAULT_USER_AGENT


class WroInitTest(utils.BaseWebRichObjectTestCase):
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
        WRO(html=html)
        self.assertFalse(mock_urlopen.called)


class WroTitleTest(utils.BaseWebRichObjectTestCase):
    def test_default_is_site_name(self):
        url = 'http://example.com'
        wro = WRO(url)
        self.assertEqual(wro.site_name, 'example.com')
    test_default_is_site_name.mock_attrs = {
        'return_value.read.return_value': '',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WroImageTest(utils.BaseWebRichObjectTestCase):
    def test_default_is_none(self):
        wro = WRO(self.url)
        self.assertEqual(wro.image, None)
    test_default_is_none.mock_attrs = {
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WroFormatUrlTest(utils.BaseWebRichObjectTestCase):
    def test_from_relative_path(self):
        wro = WRO(self.url + '/bar/')
        image_url = wro._format_url('foo.png')
        self.assertEqual(image_url, 'http://example.com/bar/foo.png')
    test_from_relative_path.mock_attrs = {
        'return_value.read.return_value': '',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_relative_path_from_root(self):
        wro = WRO(self.url + '/bar/')
        image_url = wro._format_url('/foo.png')
        self.assertEqual(image_url, 'http://example.com/foo.png')
    test_from_relative_path_from_root.mock_attrs = {
        'return_value.read.return_value': '',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }

    def test_from_relative_protocol(self):
        wro = WRO(self.url)
        image_url = wro._format_url('//example.com/foo.png')
        self.assertEqual(image_url, 'http://example.com/foo.png')
    test_from_relative_protocol.mock_attrs = {
        'return_value.read.return_value': '',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WroUrlTest(utils.BaseWebRichObjectTestCase):
    def test_default_is_base_url(self):
        wro = WRO(self.url)
        self.assertEqual(wro.url, wro.base_url)
    test_default_is_base_url.mock_attrs = {
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WroDescriptionTest(utils.BaseWebRichObjectTestCase):
    def test_default_is_none(self):
        wro = WRO(self.url)
        self.assertEqual(wro.description, None)
    test_default_is_none.mock_attrs = {
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WroAudioTest(utils.BaseWebRichObjectTestCase):
    def test_default_is_none(self):
        wro = WRO(self.url)
        self.assertEqual(wro.audio, None)
    test_default_is_none.mock_attrs = {
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WroLocaleTest(utils.BaseWebRichObjectTestCase):
    def test_default_is_none(self):
        wro = WRO(self.url)
        self.assertEqual(wro.locale, None)
    test_default_is_none.mock_attrs = {
        'return_value.read.return_value': '',
        'return_value.info.return_value.__dict__': utils.UNKNOW_RESPONSE_INFO,
    }


class WroLocaleAlternativeTest(utils.BaseWebRichObjectTestCase):
    def test_default_is_empty(self):
        wro = WRO(self.url)
        self.assertEqual(wro.locale_alternative, [])
    test_default_is_empty.mock_attrs = {
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WroSiteNameTest(utils.BaseWebRichObjectTestCase):
    def test_default_is_hostname(self):
        wro = WRO(self.url)
        self.assertEqual(wro.site_name, 'example.com')
    test_default_is_hostname.mock_attrs = {
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WroVideoTest(utils.BaseWebRichObjectTestCase):
    def test_default_is_none(self):
        wro = WRO(self.url)
        self.assertEqual(wro.video, None)
    test_default_is_none.mock_attrs = {
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WroImagesTest(utils.BaseWebRichObjectTestCase):
    def test_default_is_empty(self):
        wro = WRO(self.url)
        self.assertEqual(wro.images, [])
    test_default_is_empty.mock_attrs = {
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


class WroDeterminerTest(utils.BaseWebRichObjectTestCase):
    def test_default_is_auto(self):
        wro = WRO(self.url)
        self.assertEqual(wro.determiner, 'auto')
    test_default_is_auto.mock_attrs = {
        'return_value.read.return_value': '<html></html>',
        'return_value.info.return_value.__dict__': utils.HTML_RESPONSE_INFO,
    }


if __name__ == '__main__':
    unittest.main()
