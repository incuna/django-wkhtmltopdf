# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys

from django.conf import settings
from django.template import loader, RequestContext
from django.test import TestCase
from django.test.utils import override_settings
from django.test.client import RequestFactory
from django.utils.encoding import smart_str
import six

from wkhtmltopdf.subprocess import CalledProcessError
from wkhtmltopdf.utils import (_options_to_args, make_absolute_paths,
                               wkhtmltopdf, render_pdf_from_template,
                               render_to_temporary_file, RenderedFile)
from wkhtmltopdf.views import PDFResponse, PDFTemplateView, PDFTemplateResponse


class UnicodeContentPDFTemplateView(PDFTemplateView):
    """
    PDFTemplateView with the addition of unicode content in his context.

    Used in unicode content view testing.
    """
    def get_context_data(self, **kwargs):
        Base = super(UnicodeContentPDFTemplateView, self)
        context = Base.get_context_data(**kwargs)
        context['title'] = u'♥'
        return context


class TestUtils(TestCase):
    def setUp(self):
        # Clear standard error
        self._stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        self.factory = RequestFactory()

    def tearDown(self):
        sys.stderr = self._stderr

    def test_options_to_args(self):
        self.assertEqual(_options_to_args(), [])
        self.assertEqual(_options_to_args(heart=u'♥', verbose=True,
                                          file_name='file-name'),
                         ['--file-name', 'file-name',
                          '--heart', u'♥',
                          '--verbose'])
        self.assertEqual(_options_to_args(heart=u'♥', quiet=True,
                                          file_name='file-name'),
                         ['--file-name', 'file-name',
                          '--heart', u'♥',
                          '--quiet'])
        self.assertEqual(_options_to_args(heart=u'♥', quiet=False,
                                          file_name='file-name'),
                         ['--file-name', 'file-name',
                          '--heart', u'♥'])

    def test_wkhtmltopdf(self):
        """Should run wkhtmltopdf to generate a PDF"""
        title = 'A test template.'
        template = loader.get_template('sample.html')
        temp_file = render_to_temporary_file(template, context={'title': title})
        try:
            # Standard call
            pdf_output = wkhtmltopdf(pages=[temp_file.name])
            self.assertTrue(pdf_output.startswith(b'%PDF'), pdf_output)

            # Single page
            pdf_output = wkhtmltopdf(pages=temp_file.name)
            self.assertTrue(pdf_output.startswith(b'%PDF'), pdf_output)

            # Unicode
            pdf_output = wkhtmltopdf(pages=[temp_file.name], title=u'♥')
            self.assertTrue(pdf_output.startswith(b'%PDF'), pdf_output)

            # Invalid arguments
            self.assertRaises(CalledProcessError,
                              wkhtmltopdf, pages=[])
        finally:
            temp_file.close()

    def test_wkhtmltopdf_with_unicode_content(self):
        """A wkhtmltopdf call should render unicode content properly"""
        title = u'♥'
        template = loader.get_template('unicode.html')
        temp_file = render_to_temporary_file(template, context={'title': title})
        try:
            pdf_output = wkhtmltopdf(pages=[temp_file.name])
            self.assertTrue(pdf_output.startswith(b'%PDF'), pdf_output)
        finally:
            temp_file.close()

    def test_render_to_temporary_file(self):
        """Should render a template to a temporary file."""
        title = 'A test template.'

        template = loader.get_template('sample.html')
        temp_file = render_to_temporary_file(template, context={'title': title})
        temp_file.seek(0)
        saved_content = smart_str(temp_file.read())
        self.assertTrue(title in saved_content)
        temp_file.close()

    def _render_file(self, template, context):
        """Helper method for testing rendered file deleted/persists tests."""
        render = RenderedFile(template=template, context=context)
        render.temporary_file.seek(0)
        saved_content = smart_str(render.temporary_file.read())

        return (saved_content, render.filename)

    def test_rendered_file_deleted_on_production(self):
        """If WKHTMLTOPDF_DEBUG=False, delete rendered file on object close."""
        title = 'A test template.'
        template = loader.get_template('sample.html')
        debug = getattr(settings, 'WKHTMLTOPDF_DEBUG', settings.DEBUG)

        saved_content, filename = self._render_file(template=template,
                                                    context={'title': title})
        # First verify temp file was rendered correctly.
        self.assertTrue(title in saved_content)

        # Then check if file is deleted when debug=False.
        self.assertFalse(debug)
        self.assertFalse(os.path.isfile(filename))

    def test_rendered_file_persists_on_debug(self):
        """If WKHTMLTOPDF_DEBUG=True, the rendered file should persist."""
        title = 'A test template.'
        template = loader.get_template('sample.html')
        with self.settings(WKHTMLTOPDF_DEBUG=True):
            debug = getattr(settings, 'WKHTMLTOPDF_DEBUG', settings.DEBUG)

            saved_content, filename = self._render_file(template=template,
                                                    context={'title': title})
            # First verify temp file was rendered correctly.
            self.assertTrue(title in saved_content)

            # Then check if file persists when debug=True.
            self.assertTrue(debug)
            self.assertTrue(os.path.isfile(filename))

    def test_render_with_null_request(self):
        """If request=None, the file should render properly."""
        title = 'A test template.'
        template = loader.get_template('sample.html')
        pdf_content = render_pdf_from_template('sample.html',
                                               header_template=None,
                                               footer_template=None,
                                               context={'title': title})

        self.assertTrue(pdf_content.startswith(b'%PDF-'))
        self.assertTrue(pdf_content.endswith(b'%%EOF\n'))

    @override_settings(STATIC_URL='/static/', STATIC_ROOT='path/to/some/dir')
    def test_make_absolute_paths(self):
        """
        Regression test for https://github.com/incuna/django-wkhtmltopdf/issues/22
        """
        content = """
            <img src="/static/foo.png"/>
            <img src="/static/bar/static/foo.png"/>
        """
        expected = """
            <img src="file:///path/to/some/dir/foo.png"/>
            <img src="file:///path/to/some/dir/bar/static/foo.png"/>
        """

        self.assertEqual(make_absolute_paths(content), expected)


class TestViews(TestCase):
    template = 'sample.html'
    context_template = 'context.html'
    footer_template = 'footer.html'
    pdf_filename = 'output.pdf'
    attached_fileheader = 'attachment; filename="{0}"'
    inline_fileheader = 'inline; filename="{0}"'

    def test_pdf_response(self):
        """Should generate correct HttpResponse object and content type."""
        # 404
        response = PDFResponse(content='', status=404)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b'')
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertFalse(response.has_header('Content-Disposition'))

        content = b'%PDF-1.4\n%%EOF'
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
        try:
            import unidecode
        except ImportError:
            filename = '?.pdf'
        else:
            filename = '.pdf'
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="{0}"'.format(filename))

        # Content as a direct output
        response = PDFResponse(content=content, filename="nospace.pdf",
            show_content_in_browser=True)
        self.assertEqual(response['Content-Disposition'],
                         'inline; filename="nospace.pdf"')
        response = PDFResponse(content=content, filename="one space.pdf",
            show_content_in_browser=True)
        self.assertEqual(response['Content-Disposition'],
                         'inline; filename="one space.pdf"')
        response = PDFResponse(content=content, filename="4'5\".pdf",
            show_content_in_browser=True)
        self.assertEqual(response['Content-Disposition'],
                         'inline; filename="4\'5.pdf"')
        response = PDFResponse(content=content, filename=u"♥.pdf",
            show_content_in_browser=True)
        try:
            import unidecode
        except ImportError:
            filename = '?.pdf'
        else:
            filename = '.pdf'
        self.assertEqual(response['Content-Disposition'],
                         'inline; filename="{0}"'.format(filename))

        # Content-Type
        response = PDFResponse(content=content,
                               content_type='application/x-pdf')
        self.assertEqual(response['Content-Type'], 'application/x-pdf')

    def test_pdf_template_response(self, show_content=False):
        """Test PDFTemplateResponse."""

        context = {'title': 'Heading'}
        request = RequestFactory().get('/')
        response = PDFTemplateResponse(request=request,
                                       template=self.template,
                                       context=context,
                                       show_content_in_browser=show_content)
        self.assertEqual(response._request, request)
        self.assertEqual(response.template_name, self.template)
        self.assertEqual(response.context_data, context)
        self.assertEqual(response.filename, None)
        self.assertEqual(response.header_template, None)
        self.assertEqual(response.footer_template, None)
        self.assertEqual(response.cmd_options, {})
        self.assertFalse(response.has_header('Content-Disposition'))

        # Render to temporary file
        template = loader.get_template(self.template)
        tempfile = render_to_temporary_file(template, context=context)
        tempfile.seek(0)
        html_content = smart_str(tempfile.read())
        self.assertTrue(html_content.startswith('<html>'))
        self.assertTrue('<h1>{title}</h1>'.format(**context)
                        in html_content)

        pdf_content = response.rendered_content
        self.assertTrue(pdf_content.startswith(b'%PDF-'))
        self.assertTrue(pdf_content.endswith(b'%%EOF\n'))

        # Footer
        cmd_options = {'title': 'Test PDF'}
        response = PDFTemplateResponse(request=request,
                                       template=self.template,
                                       context=context,
                                       filename=self.pdf_filename,
                                       show_content_in_browser=show_content,
                                       footer_template=self.footer_template,
                                       cmd_options=cmd_options)
        self.assertEqual(response.filename, self.pdf_filename)
        self.assertEqual(response.header_template, None)
        self.assertEqual(response.footer_template, self.footer_template)
        self.assertEqual(response.cmd_options, cmd_options)
        self.assertTrue(response.has_header('Content-Disposition'))

        footer_template = loader.get_template(self.footer_template)
        tempfile = render_to_temporary_file(footer_template, context=context,
                                            request=request)
        tempfile.seek(0)
        footer_content = smart_str(tempfile.read())
        footer_content = make_absolute_paths(footer_content)

        media_url = 'file://{0}/'.format(settings.MEDIA_ROOT)
        self.assertTrue(media_url in footer_content, True)

        static_url = 'file://{0}/'.format(settings.STATIC_ROOT)
        self.assertTrue(static_url in footer_content, True)

        pdf_content = response.rendered_content
        title = '\0'.join(cmd_options['title'])
        self.assertIn(six.b(title), pdf_content)

    def test_pdf_template_response_to_browser(self):
        self.test_pdf_template_response(show_content=True)

    def test_pdf_template_view(self, show_content=False):
        """Test PDFTemplateView."""

        view = PDFTemplateView.as_view(filename=self.pdf_filename,
                                       show_content_in_browser=show_content,
                                       template_name=self.template,
                                       footer_template=self.footer_template)

        # As PDF
        request = RequestFactory().get('/')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        response.render()

        fileheader = self.attached_fileheader
        if show_content:
            fileheader = self.inline_fileheader
        self.assertEqual(response['Content-Disposition'],
                         fileheader.format(self.pdf_filename))
        self.assertTrue(response.content.startswith(b'%PDF-'))
        self.assertTrue(response.content.endswith(b'%%EOF\n'))

        # As HTML
        request = RequestFactory().get('/?as=html')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        response.render()
        self.assertFalse(response.has_header('Content-Disposition'))
        self.assertTrue(response.content.startswith(b'<html>'))

        # POST
        request = RequestFactory().post('/')
        response = view(request)
        self.assertEqual(response.status_code, 405)

    def test_pdf_template_view_to_browser(self):
        self.test_pdf_template_view(show_content=True)

    def test_pdf_template_view_unicode(self, show_content=False):
        """Test PDFTemplateView with unicode content."""
        view = UnicodeContentPDFTemplateView.as_view(
            filename=self.pdf_filename,
            show_content_in_browser=show_content,
            template_name=self.template
        )

        # As PDF
        request = RequestFactory().get('/')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        response.render()

        fileheader = self.attached_fileheader
        if show_content:
            fileheader = self.inline_fileheader
        self.assertEqual(response['Content-Disposition'],
                         fileheader.format(self.pdf_filename))
        # not sure how we can test this as the contents is all encoded...
        # best we can do for the moment is check it's a pdf and it worked.
        # self.assertTrue('☃' in response.content)
        self.assertTrue(response.content.startswith(b'%PDF-'))
        self.assertTrue(response.content.endswith(b'%%EOF\n'))

    def test_pdf_template_view_unicode_to_browser(self):
        self.test_pdf_template_view_unicode(show_content=True)

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

    def _render_file(self, template, context, request=None):
        """Helper method for testing rendered file deleted/persists tests."""
        render = RenderedFile(template=template, context=context, request=request)
        render.temporary_file.seek(0)
        saved_content = smart_str(render.temporary_file.read())

        return (saved_content, render.filename)

    @override_settings(
        DEBUG=True,
        INTERNAL_IPS=['127.0.0.1'],
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                    ],
                },
            },
        ]
    )
    def test_get_context_processor_variables_debug(self, show_content=False):
        request = RequestFactory().get('/')
        template = loader.get_template(self.context_template)

        saved_content, filename = self._render_file(template=template, context={}, request=request)
        self.assertTrue('<h1>True</h1>' in saved_content)

        with override_settings(DEBUG=False):
            request = RequestFactory().get('/')
            template = loader.get_template(self.context_template)

            saved_content, filename = self._render_file(template=template, context={}, request=request)
            self.assertTrue('<h1></h1>' in saved_content)

        view = PDFTemplateView.as_view(filename=self.pdf_filename,
                                       show_content_in_browser=show_content,
                                       template_name=self.context_template,
                                       footer_template=self.footer_template)
        # As HTML
        request = RequestFactory().get('/?as=html')
        response = view(request)
        self.assertEqual(response.status_code, 200)
        response.render()
        self.assertIn(b'<h1>True</h1>', response.content)
        with override_settings(DEBUG=False):
            request = RequestFactory().get('/?as=html')
            response = view(request)
            self.assertEqual(response.status_code, 200)
            response.render()
            self.assertIn(b'<h1></h1>', response.content)

    def test_get_context_processor_variables_debug_show_content(self):
        self.test_get_context_processor_variables_debug(show_content=True)
