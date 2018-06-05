from __future__ import absolute_import

from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.generic import TemplateView

from .utils import (content_disposition_filename, render_pdf_from_template)


class PDFResponse(HttpResponse):
    """HttpResponse that sets the headers for PDF output."""

    def __init__(self, content, status=200, content_type=None,
            filename=None, show_content_in_browser=None, *args, **kwargs):

        if content_type is None:
            content_type = 'application/pdf'

        super(PDFResponse, self).__init__(content=content,
                                          status=status,
                                          content_type=content_type)
        self.set_filename(filename, show_content_in_browser)

    def set_filename(self, filename, show_content_in_browser):
        self.filename = filename
        if filename:
            fileheader = 'attachment; filename={0}'
            if show_content_in_browser:
                fileheader = 'inline; filename={0}'

            filename = content_disposition_filename(filename)
            header_content = fileheader.format(filename)
            self['Content-Disposition'] = header_content
        else:
            del self['Content-Disposition']


class PDFTemplateResponse(TemplateResponse, PDFResponse):
    """Renders a Template into a PDF using wkhtmltopdf"""

    def __init__(self, request, template, context=None,
                 status=None, content_type=None, current_app=None,
                 filename=None, show_content_in_browser=None,
                 header_template=None, footer_template=None,
                 cmd_options=None, *args, **kwargs):
        cover_template = kwargs.pop('cover_template', None)

        super(PDFTemplateResponse, self).__init__(request=request,
                                                  template=template,
                                                  context=context,
                                                  status=status,
                                                  content_type=content_type,
                                                  *args, **kwargs)
        self.set_filename(filename, show_content_in_browser)

        self.header_template = header_template
        self.footer_template = footer_template
        self.cover_template = cover_template
        if cmd_options is None:
            cmd_options = {}
        self.cmd_options = cmd_options

    @property
    def rendered_content(self):
        """Returns the freshly rendered content for the template and context
        described by the PDFResponse.

        This *does not* set the final content of the response. To set the
        response content, you must either call render(), or set the
        content explicitly using the value of this property.
        """
        cmd_options = self.cmd_options.copy()
        return render_pdf_from_template(
            self.resolve_template(self.template_name),
            self.resolve_template(self.header_template),
            self.resolve_template(self.footer_template),
            context=self.resolve_context(self.context_data),
            request=self._request,
            cmd_options=cmd_options,
            cover_template=self.resolve_template(self.cover_template)

        )

class PDFTemplateView(TemplateView):
    """Class-based view for HTML templates rendered to PDF."""

    # Filename for downloaded PDF. If None, the response is inline.
    filename = 'rendered_pdf.pdf'

    # Send file as attachement. If True render content in the browser.
    show_content_in_browser = False

    # Filenames for the content, header, and footer templates.
    template_name = None
    header_template = None
    footer_template = None
    cover_template = None

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

        if issubclass(self.response_class, PDFTemplateResponse):
            if filename is None:
                filename = self.get_filename()

            if cmd_options is None:
                cmd_options = self.get_cmd_options()

            return super(PDFTemplateView, self).render_to_response(
                context=context, filename=filename,
                show_content_in_browser=self.show_content_in_browser,
                header_template=self.header_template,
                footer_template=self.footer_template,
                cmd_options=cmd_options,
                cover_template=self.cover_template,
                **response_kwargs
            )
        else:
            return super(PDFTemplateView, self).render_to_response(
                context=context,
                **response_kwargs
            )
