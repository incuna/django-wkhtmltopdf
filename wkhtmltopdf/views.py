from __future__ import absolute_import

from tempfile import NamedTemporaryFile
import re

from django.conf import settings
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.generic import TemplateView

from .utils import (content_disposition_filename, override_settings,
                    pathname2fileurl, wkhtmltopdf)


class PDFResponse(HttpResponse):
    """HttpResponse that sets the headers for PDF output."""

    def __init__(self, content, mimetype=None, status=200,
                 content_type=None, filename=None, *args, **kwargs):

        if content_type is None:
            content_type = 'application/pdf'

        super(PDFResponse, self).__init__(content=content,
                                          mimetype=mimetype,
                                          status=status,
                                          content_type=content_type)
        self.set_filename(filename)

    def set_filename(self, filename):
        self.filename = filename
        if filename:
            filename = content_disposition_filename(filename)
            header_content = 'attachment; filename={0}'.format(filename)
            self['Content-Disposition'] = header_content
        else:
            del self['Content-Disposition']


class PDFTemplateResponse(TemplateResponse, PDFResponse):
    """Renders a Template into a PDF using wkhtmltopdf"""

    def __init__(self, request, template, context=None, mimetype=None,
                 status=None, content_type=None, current_app=None,
                 filename=None, header_template=None, footer_template=None,
                 cmd_options=None, override_settings=None,
                 *args, **kwargs):

        super(PDFTemplateResponse, self).__init__(request=request,
                                                  template=template,
                                                  context=context,
                                                  mimetype=mimetype,
                                                  status=status,
                                                  content_type=content_type,
                                                  current_app=None,
                                                  *args, **kwargs)
        self.set_filename(filename)

        self.header_template = header_template
        self.footer_template = footer_template

        if cmd_options is None:
            cmd_options = {}
        self.cmd_options = cmd_options

        self.override_settings = override_settings

    def render_to_temporary_file(self, template_name, mode='w+b', bufsize=-1,
                                 suffix='', prefix='tmp', dir=None,
                                 delete=True):
        template = self.resolve_template(template_name)

        # Since many things require a sensible settings.MEDIA_URL and
        # settings.STATIC_URL, including TEMPLATE_CONTEXT_PROCESSORS;
        # the settings themselves need to be overridden when rendering.
        #
        # This allows django-wkhtmltopdf to play nicely with the
        # staticfiles app, for instance.
        with override_settings(**self.get_override_settings()):
            context = self.resolve_context(self.context_data)
            content = template.render(context)

        tempfile = NamedTemporaryFile(mode=mode, bufsize=bufsize,
                                      suffix=suffix, prefix=prefix,
                                      dir=dir, delete=delete)
        try:
            tempfile.write(content)
            tempfile.flush()
            return tempfile
        except:
            # Clean-up tempfile if an Exception is raised.
            tempfile.close()
            raise

    def convert_to_pdf(self, filename,
                       header_filename=None, footer_filename=None):
        cmd_options = self.cmd_options.copy()
        # Clobber header_html and footer_html only if filenames are
        # provided. These keys may be in self.cmd_options as hardcoded
        # static files.
        if header_filename is not None:
            cmd_options['header_html'] = header_filename
        if footer_filename is not None:
            cmd_options['footer_html'] = footer_filename
        return wkhtmltopdf(pages=[filename], **cmd_options)

    @property
    def rendered_content(self):
        """Returns the freshly rendered content for the template and context
        described by the PDFResponse.

        This *does not* set the final content of the response. To set the
        response content, you must either call render(), or set the
        content explicitly using the value of this property.
        """
        debug = getattr(settings, 'WKHTMLTOPDF_DEBUG', settings.DEBUG)

        input_file = header_file = footer_file = None
        header_filename = footer_filename = None

        try:
            input_file = self.render_to_temporary_file(
                template_name=self.template_name,
                prefix='wkhtmltopdf', suffix='.html',
                delete=(not debug)
            )

            if self.header_template:
                header_file = self.render_to_temporary_file(
                    template_name=self.header_template,
                    prefix='wkhtmltopdf', suffix='.html',
                    delete=(not debug)
                )
                header_filename = header_file.name

            if self.footer_template:
                footer_file = self.render_to_temporary_file(
                    template_name=self.footer_template,
                    prefix='wkhtmltopdf', suffix='.html',
                    delete=(not debug)
                )
                footer_filename = footer_file.name

            return self.convert_to_pdf(filename=input_file.name,
                                       header_filename=header_filename,
                                       footer_filename=footer_filename)
        finally:
            # Clean up temporary files
            for f in filter(None, (input_file, header_file, footer_file)):
                f.close()

    def get_override_settings(self):
        """Returns a dictionary of settings to override for response_class"""
        overrides = {
            'MEDIA_ROOT': settings.MEDIA_ROOT,
            'MEDIA_URL': settings.MEDIA_URL,
            'STATIC_ROOT': settings.STATIC_ROOT,
            'STATIC_URL': settings.STATIC_URL,
        }
        if self.override_settings is not None:
            overrides.update(self.override_settings)

        has_scheme = re.compile(r'^[^:/]+://')

        # If MEDIA_URL doesn't have a scheme, we transform it into a
        # file:// URL based on MEDIA_ROOT.
        urls = [('MEDIA_URL', 'MEDIA_ROOT'),
                ('STATIC_URL', 'STATIC_ROOT')]
        for url, root in urls:
            if not has_scheme.match(overrides[url]):
                overrides[url] = pathname2fileurl(overrides[root])
                if not overrides[url].endswith('/'):
                    overrides[url] += '/'

        return overrides


class PDFTemplateView(TemplateView):
    """Class-based view for HTML templates rendered to PDF."""

    # Filename for downloaded PDF. If None, the response is inline.
    filename = 'rendered_pdf.pdf'

    # Filenames for the content, header, and footer templates.
    template_name = None
    header_template = None
    footer_template = None

    # TemplateResponse classes for PDF and HTML
    response_class = PDFTemplateResponse
    html_response_class = TemplateResponse

    # Command-line options to pass to wkhtmltopdf
    cmd_options = {
        # 'orientation': 'portrait',
        # 'collate': True,
        # 'quiet': None,
    }

    def __init__(self, *args, **kwargs):
        super(PDFTemplateView, self).__init__(*args, **kwargs)

        # Copy self.cmd_options to prevent clobbering the class-level object.
        self.cmd_options = self.cmd_options.copy()

    def get(self, request, *args, **kwargs):
        response_class = self.response_class
        try:
            if request.GET.get('as', '') == 'html':
                # Use the html_response_class if HTML was requested.
                self.response_class = self.html_response_class
            return super(PDFTemplateView, self).get(request,
                                                    *args, **kwargs)
        finally:
            # Remove self.response_class
            self.response_class = response_class

    def get_filename(self):
        return self.filename

    def get_cmd_options(self):
        return self.cmd_options

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a PDF response with a template rendered with the given context.
        """
        filename = response_kwargs.pop('filename', None)
        cmd_options = response_kwargs.pop('cmd_options', None)
        override_settings = response_kwargs.pop('override_settings', None)

        if issubclass(self.response_class, PDFTemplateResponse):
            if filename is None:
                filename = self.get_filename()

            if cmd_options is None:
                cmd_options = self.get_cmd_options()

            return super(PDFTemplateView, self).render_to_response(
                context=context, filename=filename,
                header_template=self.header_template,
                footer_template=self.footer_template,
                cmd_options=cmd_options, override_settings=override_settings,
                **response_kwargs
            )
        else:
            return super(PDFTemplateView, self).render_to_response(
                context=context,
                **response_kwargs
            )
