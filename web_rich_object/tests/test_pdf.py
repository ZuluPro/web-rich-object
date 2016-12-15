import unittest
from io import BytesIO
from datetime import datetime, date
from xhtml2pdf import pisa
from web_rich_object.tests import utils
from web_rich_object.api import (
    WebRichObject as WRO,
    DEFAULT_USER_AGENT
)


def create_pdf(meta=None):
    pdf_file = BytesIO()
    pisa.CreatePDF("<html>FOO</html>", dest=pdf_file, context_meta=meta)
    pdf_file.seek(0)
    return pdf_file


class PdfTitleTest(utils.BaseWebRichObjectTestCase):
    def test_from_meta(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.title, 'test title')
    test_from_meta.mock_attrs = {
        'return_value.read.return_value': create_pdf(meta={'title': 'test title'}).read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }

    def test_from_filename(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.title, 'doc.pdf')

        wro = WRO('http://example.com/doc.pdf?version=1')
        self.assertEqual(wro.title, 'doc.pdf')
    test_from_filename.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }

    def test_not_found(self):
        wro = WRO('http://example.com/doc.pdf/')
        self.assertEqual(wro.title, 'example.com')
    test_not_found.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfTypeTest(utils.BaseWebRichObjectTestCase):
    def test_is_application(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.type, 'application')
    test_is_application.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfSubtypeTest(utils.BaseWebRichObjectTestCase):
    def test_is_pdf(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.subtype, 'pdf')
    test_is_pdf.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfImageTest(utils.BaseWebRichObjectTestCase):
    def test_no_image(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertIsNone(wro.image)
    test_no_image.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfUrlTest(utils.BaseWebRichObjectTestCase):
    def test_is_default(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.url, 'http://example.com/doc.pdf')
    test_is_default.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfGeneratorTest(utils.BaseWebRichObjectTestCase):
    def test_from_meta_creator(self):
        self.skipTest("xhtmlpdf can't create this metadata")
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.generator, 'foo')
    test_from_meta_creator.mock_attrs = {
        'return_value.read.return_value': create_pdf({'Creator': 'foo'}).read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }

    def test_from_meta_producer(self):
        self.skipTest("xhtmlpdf can't create this metadata")
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.generator, 'bar')
    test_from_meta_creator.mock_attrs = {
        'return_value.read.return_value': create_pdf({'Producer': 'bar'}).read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }

    def test_not_found(self):
        self.skipTest("xhtmlpdf can't suppress this metadata")
        wro = WRO('http://example.com/doc.pdf')
        self.assertIsNone(wro.generator)
    test_not_found.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfDescriptionTest(utils.BaseWebRichObjectTestCase):
    def test_from_meta_subject(self):
        self.skipTest("xhtmlpdf can't suppress this metadata")
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.description, 'foo')
    test_from_meta_subject.mock_attrs = {
        'return_value.read.return_value': create_pdf({'Subject': 'foo'}).read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }

    def test_not_found(self):
        self.skipTest("xhtmlpdf can't suppress this metadata")
        wro = WRO('http://example.com/doc.pdf')
        self.assertIsNone(wro.description)
    test_not_found.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfSiteNameTest(utils.BaseWebRichObjectTestCase):
    def test_not_found(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.site_name, 'example.com')
    test_not_found.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfImagesTest(utils.BaseWebRichObjectTestCase):
    def test_not_found(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.images, [])
    test_not_found.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfAuthorTest(utils.BaseWebRichObjectTestCase):
    def test_from_meta_author(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.author, 'foo')
    test_from_meta_author.mock_attrs = {
        'return_value.read.return_value': create_pdf({'author': 'foo'}).read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }

    def test_not_found(self):
        self.skipTest("xhtmlpdf can't suppress this metadata")
        wro = WRO('http://example.com/doc.pdf')
        self.assertIsNone(wro.author)
    test_not_found.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfCreatedTimeTest(utils.BaseWebRichObjectTestCase):
    def test_from_meta_creation_date(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertIsInstance(wro.created_time, datetime)
        self.assertEqual(date.today().month, wro.created_time.date().month)
        self.assertEqual(date.today().year, wro.created_time.date().year)
    test_from_meta_creation_date.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }

    def test_not_found(self):
        self.skipTest("xhtmlpdf can't suppress this metadata")
        wro = WRO('http://example.com/doc.pdf')
        self.assertIsNone(wro.created_time)
    test_not_found.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfPublishedTimeTest(utils.BaseWebRichObjectTestCase):
    def test_not_found(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertIsNone(wro.published_time)
    test_not_found.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfModifiedTimeTest(utils.BaseWebRichObjectTestCase):
    def test_from_meta_mod_date(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertIsInstance(wro.modified_time, datetime)
        self.assertEqual(date.today().year, wro.created_time.date().year)
        self.assertEqual(date.today().month, wro.created_time.date().month)
    test_from_meta_mod_date.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }

    def test_not_found(self):
        self.skipTest("xhtmlpdf can't suppress this metadata")
        wro = WRO('http://example.com/doc.pdf')
        self.assertIsNone(wro.modified_time)
    test_not_found.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


class PdfTagsTest(utils.BaseWebRichObjectTestCase):
    def test_from_meta_keywords(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.tags, ['foo', 'bar'])
    test_from_meta_keywords.mock_attrs = {
        'return_value.read.return_value': create_pdf({'keywords': 'foo bar'}).read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }

    def test_from_meta_keywords_empty(self):
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.tags, [])
    test_from_meta_keywords_empty.mock_attrs = {
        'return_value.read.return_value': create_pdf({'keywords': ''}).read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }

    def test_not_found(self):
        self.skipTest("xhtmlpdf can't suppress this metadata")
        wro = WRO('http://example.com/doc.pdf')
        self.assertEqual(wro.tags, [])
    test_not_found.mock_attrs = {
        'return_value.read.return_value': create_pdf().read(),
        'return_value.info.return_value.__dict__': utils.PDF_RESPONSE_INFO,
    }


if __name__ == '__main__':
    unittest.main()
