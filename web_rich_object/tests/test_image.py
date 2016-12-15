import unittest
from web_rich_object.tests import utils
from web_rich_object.api import WebRichObject as WRO


class ImageTypeTest(utils.BaseWebRichObjectTestCase):
    url = 'http://example.com'

    def test_from_headers(self):
        wro = WRO(self.url)
        self.assertEqual(wro.type, 'image')
    test_from_headers.mock_attrs = {
        'return_value.read.return_value': b'foo',
        'return_value.info.return_value.__dict__': utils.IMAGE_RESPONSE_INFO,
    }


if __name__ == '__main__':
    unittest.main()
