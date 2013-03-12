# -*- coding: utf-8 -*-

from __future__ import absolute_import

import os
import sys
from tempfile import gettempdir

from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory

from wkhtmltopdf.subprocess import CalledProcessError
from wkhtmltopdf.utils import (_options_to_args, override_settings,
    pathname2fileurl, wkhtmltopdf)
from wkhtmltopdf.views import PDFResponse, PDFTemplateView, PDFTemplateResponse


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

    def test_pathname2fileurl(self):
        self.assertEqual(pathname2fileurl('/'),
                         'file:///')
        self.assertEqual(pathname2fileurl('/invalid.txt'),
                         'file:///invalid.txt')
        self.assertEqual(pathname2fileurl('invalid.txt'),
                         'file:///invalid.txt')

        # Empty filenames are meaningless
        self.assertRaises(ValueError, pathname2fileurl, '')
        self.assertRaises(ValueError, pathname2fileurl, None)

        # Directories have slashes at the end
        tempdir = gettempdir()
        self.assertEqual(pathname2fileurl(tempdir),
                         'file://{0}/'.format(tempdir))
        # Slashes are preserved
        self.assertEqual(pathname2fileurl(os.path.join(tempdir, 'invalid', '')),
                         'file://{0}/invalid/'.format(tempdir))
        # Regular files don't get slashes
        self.assertEqual(pathname2fileurl(os.path.join(tempdir, 'invalid.txt')),
                         'file://{0}/invalid.txt'.format(tempdir))

        # Pathnames are canonicalized
        self.assertEqual(pathname2fileurl('/foo//bar///baz/'),
                         'file:///foo/bar/baz/')
        self.assertEqual(pathname2fileurl('/foo/bar/../baz/'),
                         'file:///foo/baz/')
        self.assertEqual(pathname2fileurl('/foo/../../../'),
                         'file:///')

        # Pathnames that are actually URLs are untouched
        self.assertEqual(pathname2fileurl('http://example.com/'),
                         'http://example.com/')
        self.assertEqual(pathname2fileurl('file://{0}'.format(tempdir)),
                         'file://{0}'.format(tempdir))

        # Unless we set ignore_url=False
        self.assertEqual(pathname2fileurl('http://example.com/',
                                          ignore_url=False),
                         'file:///http%3A//example.com/')

        # Unicode
        self.assertEqual(pathname2fileurl(u'♥.txt'), 'file:///%E2%99%A5.txt')

        # We really do ignore Unicode URLs. If that is a general problem, we
        # can solve it later.
        self.assertEqual(pathname2fileurl(u'http://example.com/♥.txt'),
                         u'http://example.com/♥.txt')

    def test_wkhtmltopdf(self):
        """Should run wkhtmltopdf to generate a PDF"""
        title = 'A test template.'
        response = PDFTemplateResponse(self.factory.get('/'), None, context={'title': title})
        temp_file = response.render_to_temporary_file('sample.html')
        try:
            # Standard call
            pdf_output = wkhtmltopdf(pages=[temp_file.name])
            self.assertTrue(pdf_output.startswith('%PDF'), pdf_output)

            # Single page
            pdf_output = wkhtmltopdf(pages=temp_file.name)
            self.assertTrue(pdf_output.startswith('%PDF'), pdf_output)

            # Unicode
            pdf_output = wkhtmltopdf(pages=[temp_file.name],
                                     cmd_args=['--title', u'♥'])
            self.assertTrue(pdf_output.startswith('%PDF'), pdf_output)

            # Invalid arguments
            self.assertRaises(CalledProcessError,
                              wkhtmltopdf, pages=[])
        finally:
            temp_file.close()

    def test_PDFTemplateResponse_render_to_temporary_file(self):
        """Should render a template to a temporary file."""
        title = 'A test template.'
        response = PDFTemplateResponse(self.factory.get('/'), None, context={'title': title})
        temp_file = response.render_to_temporary_file('sample.html')
        temp_file.seek(0)
        saved_content = temp_file.read()
        self.assertTrue(title in saved_content)
        temp_file.close()


class TestViews(TestCase):
    template = 'sample.html'
    footer_template = 'footer.html'
    pdf_filename = 'output.pdf'
    attached_fileheader = 'attachment; filename="{0}"'
    inline_fileheader = 'inline; filename="{0}"'

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
        self.assertEqual(response['Content-Disposition'],
                         'inline; filename="?.pdf"')

        # Content-Type
        response = PDFResponse(content=content,
                               content_type='application/x-pdf')
        self.assertEqual(response['Content-Type'], 'application/x-pdf')
        response = PDFResponse(content=content,
                               mimetype='application/x-pdf')
        self.assertEqual(response['Content-Type'], 'application/x-pdf')

    def test_pdf_template_response(self, show_content=False):
        """Test PDFTemplateResponse."""
        # Override settings here to allow tests to run within another Django
        # project.
        with override_settings(
            MEDIA_URL='/media/',
            MEDIA_ROOT='/tmp/media/',
            STATIC_URL='/static/',
            STATIC_ROOT='/tmp/static/',
            TEMPLATE_CONTEXT_PROCESSORS=[
                'django.core.context_processors.media',
                'django.core.context_processors.static',
            ],
            TEMPLATE_LOADERS=['django.template.loaders.filesystem.Loader'],
            TEMPLATE_DIRS=[os.path.join(os.path.dirname(__file__),
                                        '_testproject', 'templates')],
            WKHTMLTOPDF_DEBUG=False,
        ):
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
            self.assertEqual(response.cmd_args, [])
            self.assertFalse(response.has_header('Content-Disposition'))

            # Render to temporary file
            tempfile = response.render_to_temporary_file(self.template)
            tempfile.seek(0)
            html_content = tempfile.read()
            self.assertTrue(html_content.startswith('<html>'))
            self.assertTrue('<h1>{title}</h1>'.format(**context)
                            in html_content)

            pdf_content = response.rendered_content
            self.assertTrue(pdf_content.startswith('%PDF-'))
            self.assertTrue(pdf_content.endswith('%%EOF\n'))

            # Footer
            cmd_args = ['--title', 'Test PDF']
            response = PDFTemplateResponse(request=request,
                                           template=self.template,
                                           context=context,
                                           filename=self.pdf_filename,
                                           show_content_in_browser=show_content,
                                           footer_template=self.footer_template,
                                           cmd_args=cmd_args)
            self.assertEqual(response.filename, self.pdf_filename)
            self.assertEqual(response.header_template, None)
            self.assertEqual(response.footer_template, self.footer_template)
            self.assertEqual(response.cmd_args, cmd_args)
            self.assertTrue(response.has_header('Content-Disposition'))

            tempfile = response.render_to_temporary_file(self.footer_template)
            tempfile.seek(0)
            footer_content = tempfile.read()

            media_url = 'file://{0}'.format(settings.MEDIA_ROOT)
            self.assertTrue(
                media_url in footer_content,
                "{0!r} not in {1!r}".format(media_url, footer_content)
            )

            # Non-URLs should not be replaced by accident.
            media_url = '/media/sample_image_not_existing.png does not exist'
            self.assertTrue(
                media_url in footer_content,
                "{0!r} not in {1!r}".format(media_url, footer_content)
            )

            static_url = 'file://{0}'.format(settings.STATIC_ROOT)
            self.assertTrue(
                static_url in footer_content,
                "{0!r} not in {1!r}".format(static_url, footer_content)
            )

            pdf_content = response.rendered_content
            self.assertTrue('\0'.join('{title}'.format(title=cmd_args[1]))
                            in pdf_content)

            # Override settings
            response = PDFTemplateResponse(request=request,
                                           template=self.template,
                                           context=context,
                                           filename=self.pdf_filename,
                                           footer_template=self.footer_template,
                                           cmd_args=cmd_args,
                                           override_settings={
                                               'STATIC_URL': 'file:///tmp/s/'
                                           })
            tempfile = response.render_to_temporary_file(self.footer_template)
            tempfile.seek(0)
            footer_content = tempfile.read()

            static_url = '{0}sample_js_not_existing.js'.format('file:///tmp/s/')
            self.assertTrue(
                static_url in footer_content,
                "{0!r} not in {1!r}".format(static_url, footer_content)
            )

            # Settings were not changed, only context variables
            self.assertEqual(settings.STATIC_URL, '/static/')

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

    def test_pdf_template_view_to_browser(self):
        self.test_pdf_template_view(show_content=True)

    def test_pdf_template_view_unicode(self, show_content=False):
        """Test PDFTemplateView."""

        view = PDFTemplateView.as_view(filename=self.pdf_filename,
                                       show_content_in_browser=show_content,
                                       template_name=self.template)

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
        self.assertTrue(response.content.startswith('%PDF-'))
        self.assertTrue(response.content.endswith('%%EOF\n'))

    def test_pdf_template_view_unicode_to_browser(self):
        self.test_pdf_template_view_unicode(show_content=True)

    def test_get_cmd_args(self):
        # Default cmd_args
        view = PDFTemplateView()
        self.assertEqual(view.cmd_args, PDFTemplateView.cmd_args)
        self.assertEqual(PDFTemplateView.cmd_args, [])

        # Instantiate with new cmd_args
        cmd_args = ['--orientation', 'landscape']
        view = PDFTemplateView(cmd_args=cmd_args)
        self.assertEqual(view.cmd_args, cmd_args)
        self.assertEqual(PDFTemplateView.cmd_args, [])

        # Update local instance of cmd_args
        view = PDFTemplateView()
        view.cmd_args.extend(cmd_args)
        self.assertEqual(view.cmd_args, cmd_args)
        self.assertEqual(PDFTemplateView.cmd_args, [])
