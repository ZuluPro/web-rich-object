import unittest
from copy import deepcopy
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class BaseWebRichObjectTestCase(unittest.TestCase):
    url = 'http://example.com'

    def _get_mock_attrs(self):
        func = getattr(self, self._testMethodName)
        return getattr(func, 'mock_attrs', None)

    def setUp(self):
        mock_attrs = self._get_mock_attrs()
        if mock_attrs is not None:
            self.patch = patch('web_rich_object.api.urlopen', **mock_attrs)
            self.patch.start()

    def tearDown(self):
        if self._get_mock_attrs() is not None:
            self.patch.stop()

HTML_RESPONSE_INFO = {
    'dict': {
        'accept-ranges': 'bytes',
        'cache-control': 'max-age=900',
        'connection': 'close',
        'content-length': '59593',
        'content-type': 'text/html; charset=UTF-8',
        'date': 'Sat, 17 Dec 2016 20:52:48 GMT',
        'expires': 'Sat, 17 Dec 2016 21:06:53 GMT',
        'server': 'Apache',
        'x-adobe-content': 'AEM',
        'x-ua-compatible': 'IE=11'
    },
    'encodingheader': None,
    'fp': None,
    'headers': [
        'Server: Apache\r\n',
        'X-UA-Compatible: IE=11\r\n',
        'X-Adobe-Content: AEM\r\n',
        'Accept-Ranges: bytes\r\n',
        'Cache-Control: max-age=900\r\n',
        'Expires: Sat, 17 Dec 2016 21:06:53 GMT\r\n',
        'Content-Type: text/html; charset=UTF-8\r\n',
        'Date: Sat, 17 Dec 2016 20:52:48 GMT\r\n',
        'Content-Length: 59593\r\n',
        'Content-Language: PT\r\n',
        'Connection: close\r\n'
    ],
    'maintype': 'text',
    'plist': ['charset=UTF-8'],
    'plisttext': '; charset=UTF-8',
    'seekable': 0,
    'startofbody': None,
    'startofheaders': None,
    'status': '',
    'subtype': 'html',
    'type': 'text/html',
    'typeheader': 'text/html; charset=UTF-8',
    'unixfrom': ''
}

PDF_RESPONSE_INFO = deepcopy(HTML_RESPONSE_INFO)
PDF_RESPONSE_INFO['maintype'] = 'application'
PDF_RESPONSE_INFO['type'] = 'application'
PDF_RESPONSE_INFO['subtype'] = 'pdf'

IMAGE_RESPONSE_INFO = {
    'dict': {
        'cache-control': 'public, max-age=315360000',
        'cf-cache-status': 'MISS',
        'cf-ray': '312f513938bc6224-LIS',
        'connection': 'close',
        'content-length': '12141',
        'content-type': 'image/png',
        'date': 'Sun, 18 Dec 2016 02:52:11 GMT',
        'etag': '"63045090f550f37601888be65832f3e6"',
        'expires': 'Wed, 16 Dec 2026 02:52:11 GMT',
        'last-modified': 'Tue, 18 Aug 2015 14:43:38 GMT',
        'server': 'cloudflare-nginx',
        'set-cookie': '__cfduid=dd3b9155f31aac201599f9a237f5457e41482029531; expires=Mon, 18-Dec-17 02:52:11 GMT; path=/; domain=.imgur.com; HttpOnly',
        'vary': 'Accept-Encoding',
        'x-amz-storage-class': 'REDUCED_REDUNDANCY',
        'x-amz-version-id': '4fxFOV0qAhyGrAviTh37dKrZfC5qu2hL'
    },
    'encodingheader': None,
    'fp': None,
    'headers': [
        'Date: Sun, 18 Dec 2016 02:52:11 GMT\r\n',
        'Content-Type: image/png\r\n',
        'Content-Length: 12141\r\n',
        'Connection: close\r\n',
        'Set-Cookie: __cfduid=dd3b9155f31aac201599f9a237f5457e41482029531; expires=Mon, 18-Dec-17 02:52:11 GMT; path=/; domain=.imgur.com; HttpOnly\r\n',
        'Cache-Control: public, max-age=315360000\r\n',
        'ETag: "63045090f550f37601888be65832f3e6"\r\n',
        'Expires: Wed, 16 Dec 2026 02:52:11 GMT\r\n',
        'Last-Modified: Tue, 18 Aug 2015 14:43:38 GMT\r\n',
        'x-amz-storage-class: REDUCED_REDUNDANCY\r\n',
        'x-amz-version-id: 4fxFOV0qAhyGrAviTh37dKrZfC5qu2hL\r\n',
        'CF-Cache-Status: MISS\r\n',
        'Vary: Accept-Encoding\r\n',
        'Server: cloudflare-nginx\r\n',
        'CF-RAY: 312f513938bc6224-LIS\r\n'
    ],
    'maintype': 'image',
    'plist': [],
    'plisttext': '',
    'seekable': 0,
    'startofbody': None,
    'startofheaders': None,
    'status': '',
    'subtype': 'png',
    'type': 'image/png',
    'typeheader': 'image/png',
    'unixfrom': ''
}

UNKNOW_RESPONSE_INFO = deepcopy(HTML_RESPONSE_INFO)
del PDF_RESPONSE_INFO['headers'][UNKNOW_RESPONSE_INFO['headers'].index('Content-Language: PT\r\n')]
