Usage
=====

The :py:class:`PDFTemplateView` is a Django class-based view.
By default, it uses :py:class:`PDFTemplateResponse` to render an HTML
template to PDF.
It accepts the following class attributes:

:py:attr:`template_name`
    The full name of a template to use as the body of the PDF.

:py:attr:`header_template`
    Optional.
    The full name of a template to use as the header on each page.

:py:attr:`footer_template`
    Optional.
    The full name of a template to use as the footer on each page.

:py:attr:`filename`
    The filename to use when responding with an attachment containing
    the PDF.
    Default is ``'rendered_pdf.pdf'``.

    If ``None``, the view returns the PDF output inline,
    not as an attachment.

:py:attr:`response_class`
    The response class to be returned by :py:meth:`render_to_response`
    method.
    Default is :py:class:`PDFTemplateResponse`.

:py:attr:`html_response_class`
    The response class to be returned by :py:meth:`render_to_response`
    method, when rendering as HTML.
    See note below.
    Default is :py:class:`TemplateResponse`.

:py:attr:`cmd_options`
    The dictionary of command-line arguments passed to the underlying
    ``wkhtmltopdf`` binary.
    Default is ``{}``.

    wkhtmltopdf options can be found by running ``wkhtmltopdf --help``.
    Unfortunately they don't provide hosted documentation.

.. note::

    For convenience in development you can add the GET arg ``?as=html`` to the
    end of your URL to render the PDF as a web page.


Simple Example
--------------

Point a URL at :py:class:`PDFTemplateView`:

.. code-block:: python

    from django.conf.urls.defaults import *
    from wkhtmltopdf.views import PDFTemplateView


    urlpatterns = patterns('',
        # ...
        url(r'^pdf/$', PDFTemplateView.as_view(template_name='my_template.html',
                                               filename='my_pdf.pdf'), name='pdf'),
        # ...
    )

Or use in a view:

.. code-block:: python

    from django.shortcuts import render_to_response
    from wkhtmltopdf import render_to_pdf
    
    def pdf(request):
        context.update({'objects': ModelA.objects.filter(p_id=100)})
    
        kwargs = {}
        if request.GET and request.GET.get('as', '') == 'html':
            render_to = render_to_response
        else:
            render_to = render_to_pdf
            kwargs.update(dict(
                filename='model-a.pdf',
                margin_top=0,
                margin_right=0,
                margin_bottom=0,
                margin_left=0))
    
        return render_to('pdf.html', context, **kwargs)


Advanced Example
----------------

Point a URL (as above) at your own view that subclasses
:py:class:`PDFTemplateView`
and override the sections you need to.

.. code-block:: python

    from wkhtmltopdf.views import PDFTemplateView


    class MyPDF(PDFTemplateView):
        filename = 'my_pdf.pdf'
        template_name = 'my_template.html'
        cmd_options = {
            'margin-top': 3,
        }

Unicode characters
------------------

Templates containing utf-8 characters should be supported. You will need to
ensure that you set the content type in your template file for `wkhtmltopdf` to
interpret it properly.

.. code-block:: html

    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
