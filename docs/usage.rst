Usage
=====

The ``PDFTemplateView`` takes a selection of variables, most of which get passed
to the underlying wkhtmltopdf binary. The exceptions are:

* filename
* footer_template
* header_template
* response
* template_name

wkhtmltopdf options can be found by running ``wkhtmltopdf --help``. Unfortunately
they don't provide hosted documentation. Any variables you pass to django-wkhtmltopdf
need to be underscored. They will be converted to hyphenated variables for use with
the wkhtmltopdf binary.

.. note::

    For convenience in development you can add the GET arg ``?as=html`` to the
    end of your URL to render the PDF as a web page.


Simple Example
--------------

Point a URL at PDFTemplateView:

.. code-block:: python

    from django.conf.urls.defaults import *
    from wkhtmltopdf.views import PDFTemplateView


    urlpatterns = patterns('',
        # ...
        url(r'^pdf/$', PDFTemplateView.as_view(template_name='my_template.html',
                                               filename='my_pdf.pdf'), name='pdf'),
        # ...
    )


Advanced Example
----------------

Point a URL (as above) at your own view that subclasses ``PDFTemplateView`` and
and override the sections you need to.

.. code-block:: python

    from django_wkhtmltopdf.views import PDFTemplateView


    class MyPDF(PDFTemplateView):
        filename = 'my_pdf.pdf'
        margin_top = 3
        template_name = 'my_template.html'

