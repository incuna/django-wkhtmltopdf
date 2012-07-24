# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys
import warnings

from django.test import TestCase
from django.test.client import RequestFactory

from .subprocess import CalledProcessError
from .utils import (override_settings,
                    _options_to_args, template_to_temp_file, wkhtmltopdf)
from .views import (PDFResponse, PdfResponse, PDFTemplateResponse,
                    PDFTemplateView, PdfTemplateView)


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
        """Should generate the correct HttpResponse object and mimetype"""
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

    def test_pdf_template_response(self):
        """Test PDFTemplateResponse."""
        from django.conf import settings

        with override_settings(
            MEDIA_URL='/media/',
            STATIC_URL='/static/',
            TEMPLATE_LOADERS=['django.template.loaders.filesystem.Loader'],
            TEMPLATE_DIRS=[os.path.join(os.path.dirname(__file__),
                                        '_testproject', 'templates')],
            WKHTMLTOPDF_DEBUG=False,
        ):
            # Setup sample.html
            template = 'sample.html'
            context = {'title': 'Heading'}
            request = RequestFactory().get('/')
            response = PDFTemplateResponse(request=request,
                                           template=template,
                                           context=context)
            self.assertEqual(response._request, request)
            self.assertEqual(response.template_name, template)
            self.assertEqual(response.context_data, context)
            self.assertEqual(response.filename, None)
            self.assertEqual(response.header_template, None)
            self.assertEqual(response.footer_template, None)
            self.assertEqual(response.cmd_options, {})
            self.assertFalse(response.has_header('Content-Disposition'))

            # Render to temporary file
            tempfile = response.render_to_temporary_file(template)
            tempfile.seek(0)
            html_content = tempfile.read()
            self.assertTrue(html_content.startswith('<html>'))
            self.assertTrue('<h1>{title}</h1>'.format(**context)
                            in html_content)

            pdf_content = response.rendered_content
            self.assertTrue(pdf_content.startswith('%PDF-'))
            self.assertTrue(pdf_content.endswith('%%EOF\n'))

            # Header
            filename = 'output.pdf'
            footer_template = 'footer.html'
            cmd_options = {'title': 'Test PDF'}
            response = PDFTemplateResponse(request=request,
                                           template=template,
                                           context=context,
                                           filename=filename,
                                           footer_template=footer_template,
                                           cmd_options=cmd_options)
            self.assertEqual(response.filename, filename)
            self.assertEqual(response.header_template, None)
            self.assertEqual(response.footer_template, footer_template)
            self.assertEqual(response.cmd_options, cmd_options)
            self.assertTrue(response.has_header('Content-Disposition'))

            tempfile = response.render_to_temporary_file(footer_template)
            tempfile.seek(0)
            footer_content = tempfile.read()
            self.assertTrue('MEDIA_URL = {}'.format(settings.MEDIA_URL)
                            in footer_content)
            self.assertTrue('STATIC_URL = {}'.format(settings.STATIC_URL)
                            in footer_content)

            pdf_content = response.rendered_content
            self.assertTrue('\0'.join('{title}'.format(**cmd_options))
                            in pdf_content)

    def test_pdf_template_view(self):
        """Test PDFTemplateView."""
        with override_settings(
            MEDIA_URL='/media/',
            STATIC_URL='/static/',
            TEMPLATE_LOADERS=['django.template.loaders.filesystem.Loader'],
            TEMPLATE_DIRS=[os.path.join(os.path.dirname(__file__),
                                        '_testproject', 'templates')],
            WKHTMLTOPDF_DEBUG=False,
        ):
            # Setup sample.html
            template = 'sample.html'
            filename = 'output.pdf'
            view = PDFTemplateView.as_view(filename=filename,
                                           template_name=template)

            # As PDF
            request = RequestFactory().get('/')
            response = view(request)
            self.assertEqual(response.status_code, 200)
            response.render()
            self.assertEqual(response['Content-Disposition'],
                             'attachment; filename="{}"'.format(filename))
            self.assertTrue(response.content.startswith('%PDF-'))
            self.assertTrue(response.content.endswith('%%EOF\n'))

            # As HTML
            request = RequestFactory().get('/?as=html')
            response = view(request)
            self.assertEqual(response.status_code, 200)
            response.render()
            self.assertFalse(response.has_header('Content-Disposition'))
            self.assertTrue(response.content.startswith('<html>'))

            # POST
            request = RequestFactory().post('/')
            response = view(request)
            self.assertEqual(response.status_code, 405)

    def test_get_cmd_options(self):
        # Default cmd_options
        view = PDFTemplateView()
        self.assertEqual(view.cmd_options, PDFTemplateView.cmd_options)
        self.assertEqual(PDFTemplateView.cmd_options, {})

        # Instantiate with new cmd_options
        cmd_options = {'orientation': 'landscape'}
        view = PDFTemplateView(cmd_options=cmd_options)
        self.assertEqual(view.cmd_options, cmd_options)
        self.assertEqual(PDFTemplateView.cmd_options, {})

        # Update local instance of cmd_options
        view = PDFTemplateView()
        view.cmd_options.update(cmd_options)
        self.assertEqual(view.cmd_options, cmd_options)
        self.assertEqual(PDFTemplateView.cmd_options, {})

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
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            PDFTemplateView().get_pdf_kwargs()
            self.assertEqual(len(w), 1)
            self.assertEqual(w[0].category, PendingDeprecationWarning)
            self.assertTrue(
                'get_pdf_kwargs()' in str(w[0].message),
                "'get_pdf_kwargs()' not in {!r}".format(w[0].message))
