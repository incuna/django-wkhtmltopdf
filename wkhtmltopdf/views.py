from os import remove
from re import compile

from django.conf import settings
from django.contrib.sites.models import Site
from django.template.response import HttpResponse
from django.views.generic import TemplateView

from wkhtmltopdf.utils import template_to_temp_file, wkhtmltopdf

class PdfResponse(HttpResponse):
    def __init__(self, content, filename):
        super(PdfResponse, self).__init__(content, 'application/pdf')
        self.__setitem__('Content-Disposition', 'attachment; filename=%s' % filename)


class PdfTemplateView(TemplateView):
    filename = 'rendered_pdf.pdf'
    footer_template = None
    header_template = None
    margin_bottom = 0
    margin_left = 0
    margin_right = 0
    margin_top = 0
    response = PdfResponse

    def get(self, request, context_instance=None, *args, **kwargs):
        if request.GET.get('as', '') == 'html':
            super(PdfTemplateView, self).get(request, *args, **kwargs)

        page_path = template_to_temp_file(self.template_name, self.get_context_data(), context_instance)

        tmp_files = []
        if self.header_template:
            kwargs['header_html'] = template_to_temp_file(self.header_template, self.get_context_data(), context_instance)
            tmp_files.append(kwargs['header_html'])
        if self.footer_template:
            kwargs['footer_html'] = template_to_temp_file(self.footer_template, self.get_context_data(), context_instance)
            tmp_files.append(kwargs['footer_html'])

        map(remove, tmp_files)

        kwargs.update({
            'margin_bottom': self.margin_bottom,
            'margin_left': self.margin_left,
            'margin_right': self.margin_right,
            'margin_top': self.margin_top
        })
        return self.response(wkhtmltopdf(page_path, **kwargs), self.filename)

    def get_context_data(self, **kwargs):
        context = super(PdfTemplateView, self).get_context_data(**kwargs)

        match_full_url = compile(r'^https?://')
        if not match_full_url.match(settings.STATIC_URL):
            context['STATIC_URL'] = 'http://' + Site.objects.get_current().domain + settings.STATIC_URL
        if not match_full_url.match(settings.MEDIA_URL):
            context['MEDIA_URL'] = 'http://' + Site.objects.get_current().domain + settings.MEDIA_URL

        return context

