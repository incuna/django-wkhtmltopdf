from __future__ import absolute_import

import os

from django.test import TestCase

from .utils import template_to_temp_file, wkhtmltopdf


class TestUtils(TestCase):
    def test_wkhtmltopdf(self):
        """Should run wkhtmltopdf to generate a PDF"""
        title = 'A test template.'
        temp_file = template_to_temp_file('sample.html', {'title': title})
        pdf_output = None
        try:
            pdf_output = wkhtmltopdf(pages=[temp_file])
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        self.assertTrue(pdf_output.startswith('%PDF'), pdf_output)

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
