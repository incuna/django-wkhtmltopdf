from os import remove
from re import compile

from django.conf import settings
from django.contrib.sites.models import Site
from django.template.response import HttpResponse
from django.views.generic import TemplateView

from wkhtmltopdf.utils import template_to_temp_file, wkhtmltopdf


class PDFResponse(HttpResponse):
    def __init__(self, content, filename):
        super(PDFResponse, self).__init__(content, 'application/pdf')
        self.__setitem__('Content-Disposition', 'attachment; filename=%s' % filename)


class PdfResponse(PDFResponse):
    def __init__(self, content, filename):
        warning = '''PdfResponse is deprecated in favour of PDFResponse. It will be removed in version 1.'''
        raise PendingDeprecationWarning(warning)
        super(PdfResponse, self).__init__(content, filename)


class PDFTemplateView(TemplateView):
    filename = 'rendered_pdf.pdf'
    footer_template = None
    header_template = None
    orientation = 'portrait'
    margin_bottom = 0
    margin_left = 0
    margin_right = 0
    margin_top = 0
    response = PDFResponse

    def get(self, request, context_instance=None, *args, **kwargs):
        if request.GET.get('as', '') == 'html':
            return super(PDFTemplateView, self).get(request, *args, **kwargs)

        self.context_instance = context_instance

        page_path = template_to_temp_file(self.template_name, self.get_context_data(), self.context_instance)
        pdf_kwargs = self.get_pdf_kwargs()
        return self.response(wkhtmltopdf(page_path, **pdf_kwargs), self.get_filename())

    def get_filename(self):
        return self.filename

    def get_pdf_kwargs(self):
        kwargs = {
            'margin_bottom': self.margin_bottom,
            'margin_left': self.margin_left,
            'margin_right': self.margin_right,
            'margin_top': self.margin_top,
            'orientation': self.orientation,
        }
        tmp_files = []
        if self.header_template:
            kwargs['header_html'] = template_to_temp_file(self.header_template, self.get_context_data(), self.context_instance)
            tmp_files.append(kwargs['header_html'])
        if self.footer_template:
            kwargs['footer_html'] = template_to_temp_file(self.footer_template, self.get_context_data(), self.context_instance)
            tmp_files.append(kwargs['footer_html'])
        map(remove, tmp_files)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(PDFTemplateView, self).get_context_data(**kwargs)

        match_full_url = compile(r'^https?://')
        if not match_full_url.match(settings.STATIC_URL):
            context['STATIC_URL'] = 'http://' + Site.objects.get_current().domain + settings.STATIC_URL
        if not match_full_url.match(settings.MEDIA_URL):
            context['MEDIA_URL'] = 'http://' + Site.objects.get_current().domain + settings.MEDIA_URL

        return context


class PdfTemplateView(PDFTemplateView): #TODO: Remove this in v1.0
    def as_view(cls, **initkwargs):
        warning = '''PdfTemplateView is deprecated in favour of PDFTemplateView. It will be removed in version 1.'''
        raise PendingDeprecationWarning(warning)
        return super(PdfTemplateView, cls).as_view(**initkwargs)