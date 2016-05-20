Usage
=====

The :py:class:`PDFTemplateView` is a Django class-based view.
By default, it uses :py:class:`PDFTemplateResponse` to render an HTML
template to PDF.
It accepts the following class attributes:

:py:attr:`pdf_template_name`
    The full name of a template to use as the body of the PDF.

:py:attr:`pdf_header_template`
    Optional.
    The full name of a template to use as the header on each page.

:py:attr:`pdf_footer_template`
    Optional.
    The full name of a template to use as the footer on each page.

:py:attr:`filename`
    The filename to use when responding with an attachment containing
    the PDF.
    Default is ``'rendered_pdf.pdf'``.

    If ``None``, the view returns the PDF output inline,
    not as an attachment.

:py:attr:`pdf_response_class`
    The response class to be returned by :py:meth:`render_pdf_to_response`
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

:py:attr:`pdf_default_response_is_pdf`
    Default is ``True``.

    if ``False`` the PDF only is rendered if ``?as=pdf`` GET arg was passed to end
    of your URL

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
                                               pdf_template_name='my_pdf_template.html',
                                               filename='my_pdf.pdf'), name='pdf'),
        # ...
    )


Advanced Example
----------------

Point a URL (as above) at your own view that subclasses
:py:class:`PDFTemplateView`
and override the sections you need to.

.. code-block:: python

    from wkhtmltopdf.views import PDFTemplateView


    class MyPDF(PDFTemplateView):
        filename = 'my_pdf.pdf'
        pdf_template_name = 'my_template.html'
        pdf_footer_template = 'my_default_footer_template.html'
        cmd_options = {
            'margin-top': 3,
        }

        def get_pdf_footer_template(self):
            if self.request.user.is_authenticated():
                return 'my_user_authenticated_footer_template.html'
            return self.pdf_footer_template

Unicode characters
------------------

Templates containing utf-8 characters should be supported. You will need to
ensure that you set the content type in your template file for `wkhtmltopdf` to
interpret it properly.

.. code-block:: html

    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
