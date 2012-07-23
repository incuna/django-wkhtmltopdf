# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys
import warnings

from django.test import TestCase

from .subprocess import CalledProcessError
from .utils import _options_to_args, template_to_temp_file, wkhtmltopdf
from .views import PDFResponse, PdfResponse, PdfTemplateView


class TestUtils(TestCase):
    def setUp(self):
        # Clear standard error
        self._stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')

    def tearDown(self):
        sys.stderr = self._stderr

    def test_options_to_args(self):
        self.assertEqual(_options_to_args(), [])
        self.assertEqual(_options_to_args(heart=u'♥', verbose=True,
                                          file_name='file-name'),
                         ['--file-name', 'file-name',
                          '--heart', u'♥',
                          '--verbose'])

    def test_wkhtmltopdf(self):
        """Should run wkhtmltopdf to generate a PDF"""
        title = 'A test template.'
        temp_file = template_to_temp_file('sample.html', {'title': title})
        pdf_output = None
        try:
            # Standard call
            pdf_output = wkhtmltopdf(pages=[temp_file])
            self.assertTrue(pdf_output.startswith('%PDF'), pdf_output)

            # Single page
            pdf_output = wkhtmltopdf(pages=temp_file)
            self.assertTrue(pdf_output.startswith('%PDF'), pdf_output)

            # Unicode
            pdf_output = wkhtmltopdf(pages=[temp_file], title=u'♥')
            self.assertTrue(pdf_output.startswith('%PDF'), pdf_output)

            # Invalid arguments
            self.assertRaises(CalledProcessError,
                              wkhtmltopdf, pages=[])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_template_to_temp_file(self):
        """Should render a template to a temporary file."""
        title = 'A test template.'
        temp_file = template_to_temp_file('sample.html', {'title': title})
        try:
            with open(temp_file, 'r') as f:
                saved_content = f.read()
            self.assertTrue(title in saved_content)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestViews(TestCase):
    def test_pdf_response(self):
        """Should generate the correct HttpResonse object and mimetype"""
        # 404
        response = PDFResponse(content='', status=404)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, '')
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertFalse(response.has_header('Content-Disposition'))

        content = '%PDF-1.4\n%%EOF'
        # Without filename
        response = PDFResponse(content=content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, content)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertFalse(response.has_header('Content-Disposition'))

        # With filename
        response = PDFResponse(content=content, filename="nospace.pdf")
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="nospace.pdf"')
        response = PDFResponse(content=content, filename="one space.pdf")
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="one space.pdf"')
        response = PDFResponse(content=content, filename="4'5\".pdf")
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="4\'5.pdf"')
        response = PDFResponse(content=content, filename=u"♥.pdf")
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="?.pdf"')

        # Content-Type
        response = PDFResponse(content=content,
                               content_type='application/x-pdf')
        self.assertEqual(response['Content-Type'], 'application/x-pdf')
        response = PDFResponse(content=content,
                               mimetype='application/x-pdf')
        self.assertEqual(response['Content-Type'], 'application/x-pdf')

    def test_deprecated(self):
        """Should warn when using deprecated views."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            PdfTemplateView()
            self.assertEqual(len(w), 1)
            self.assertEqual(w[0].category, PendingDeprecationWarning)
            self.assertTrue(
                'PDFTemplateView' in str(w[0].message),
                "'PDFTemplateView' not in {!r}".format(w[0].message))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            PdfResponse(None, None)
            self.assertEqual(len(w), 1)
            self.assertEqual(w[0].category, PendingDeprecationWarning)
            self.assertTrue(
                'PDFResponse' in str(w[0].message),
                "'PDFResponse' not in {!r}".format(w[0].message))
