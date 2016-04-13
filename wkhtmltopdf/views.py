from __future__ import absolute_import

import warnings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.views.generic import TemplateView

from .utils import (content_disposition_filename, render_pdf_from_template,
                    DjangoWkhtmlToPDFRemovedInNextVersionWarning)


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
        super(PDFTemplateResponse, self).__init__(request=request,
                                                  template=template,
                                                  context=context,
                                                  status=status,
                                                  content_type=content_type,
                                                  current_app=None,
                                                  *args, **kwargs)
        self.set_filename(filename, show_content_in_browser)

        self.header_template = header_template
        self.footer_template = footer_template

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
            input_template=self.resolve_template(self.template_name),
            header_template=self.resolve_template(self.header_template),
            footer_template=self.resolve_template(self.footer_template),
            context=self.resolve_context(self.context_data),
            request=self._request,
            cmd_options=cmd_options
        )


class PDFRenderMixin(object):
    """Class-based view for HTML templates rendered to PDF."""

    pdf_default_response_is_pdf = False
    # Filename for downloaded PDF. If None, the response is inline.
    filename = 'rendered_pdf.pdf'

    # Send file as attachement. If True render content in the browser.
    show_content_in_browser = False

    # Filenames for the content, header, and footer templates.
    pdf_template_name = None
    pdf_header_template = None
    pdf_footer_template = None

    # TemplateResponse classes for PDF and HTML
    pdf_response_class = PDFTemplateResponse
    html_response_class = TemplateResponse

    # Command-line options to pass to wkhtmltopdf
    cmd_options = {
        # 'orientation': 'portrait',
        # 'collate': True,
        # 'quiet': None,
    }

    def __init__(self, *args, **kwargs):
        super(PDFRenderMixin, self).__init__(*args, **kwargs)

        # Copy self.cmd_options to prevent clobbering the class-level object.
        self.cmd_options = self.cmd_options.copy()

    def get_pdf_template_name(self):
        if not self.pdf_template_name:
            raise ImproperlyConfigured(
                '{0} is missing an pdf_template_name.'
                ' Define '
                '{0}.pdf_template_name or override '
                '{0}.pdf_template_name().'.format(
                    self.__class__.__name__))
        return self.pdf_template_name

    def get_pdf_header_template(self):
        return self.pdf_header_template

    def get_pdf_footer_template(self):
        return self.pdf_footer_template

    def get_filename(self):
        return self.filename

    def get_cmd_options(self):
        return self.cmd_options

    def render_pdf_to_response(self, context, **response_kwargs):
        """
        Returns a PDF response with a template rendered with the given context.
        """
        filename = response_kwargs.pop('filename', None)
        cmd_options = response_kwargs.pop('cmd_options', None)

        if not issubclass(self.pdf_response_class, PDFTemplateResponse):
            raise ImproperlyConfigured(
                "{0}.pdf_response_class requires either a subclass of PDFTemplateResponse".format(
                    self.__class__.__name__))
        else:
            if filename is None:
                filename = self.get_filename()

            if cmd_options is None:
                cmd_options = self.get_cmd_options()

            return self.pdf_response_class(
                request=self.request,
                template=self.get_pdf_template_name(),
                context=context, filename=filename,
                show_content_in_browser=self.show_content_in_browser,
                header_template=self.get_pdf_header_template(),
                footer_template=self.get_pdf_footer_template(),
                cmd_options=cmd_options,
                **response_kwargs
            )

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('as', None) == 'pdf' or self.pdf_default_response_is_pdf:
            return self.render_pdf_to_response(context, **response_kwargs)
        else:
            return super(PDFRenderMixin, self).render_to_response(context, **response_kwargs)


class PDFTemplateView(PDFRenderMixin, TemplateView):
    #pdf_default_response_is_pdf = False
    header_template = None
    footer_template = None

    def get_pdf_template_name(self):
        if not self.pdf_template_name:
            return self.template_name
        if hasattr(self, 'template_name') and self.template_name:
            warnings.warn("Usage of template_name to define a base template to generate pdf"
                          "has been deprecated and will be "
                          "removed in next version. Please, define pdf_template_name instead",
                          DjangoWkhtmlToPDFRemovedInNextVersionWarning, stacklevel=2)
            return self.template_name
        return super(PDFTemplateView, self).get_pdf_template_name()

    def get_pdf_header_template(self):
        if not self.pdf_header_template:
            warnings.warn("Usage of header_template to define a 'header' template to generate pdf"
                          "has been deprecated and will be "
                          "removed in next version. Please, define pdf_header_template instead",
                          DjangoWkhtmlToPDFRemovedInNextVersionWarning, stacklevel=2)
            return self.header_template
        return super(PDFTemplateView, self).get_pdf_header_template()

    def get_pdf_footer_template(self):
        if not self.pdf_footer_template:
            warnings.warn("Usage of footer_template to define a 'footer' template to generate pdf"
                          "has been deprecated and will be "
                          "removed in next version. Please, define pdf_footer_template instead",
                          DjangoWkhtmlToPDFRemovedInNextVersionWarning, stacklevel=2)
            return self.footer_template
        return super(PDFTemplateView, self).get_pdf_footer_template()

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('as', None) == 'html':
            # Use the html_response_class if HTML was requested.
            return super(PDFTemplateView, self).render_to_response(context, **response_kwargs)
        else:
            return super(PDFTemplateView, self).render_pdf_to_response(context, **response_kwargs)
