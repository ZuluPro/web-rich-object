import unittest
try:
    from urllib import URLError
except ImportError:
    from urllib2 import URLError
from web_rich_object.api import WebRichObject as WRO


class HtmlTest(unittest.TestCase):
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
