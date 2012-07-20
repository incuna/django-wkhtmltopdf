# -*- coding: utf-8 -*-

from __future__ import absolute_import

from StringIO import StringIO
import os
import sys

from django.test import TestCase

from .subprocess import CalledProcessError
from .utils import _options_to_args, template_to_temp_file, wkhtmltopdf


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
