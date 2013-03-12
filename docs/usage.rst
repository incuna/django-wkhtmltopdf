Usage
=====

The :py:class:`PDFTemplateView` is a `Django class-based template view`_.
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

:py:attr:`cmd_args`
    The list of command-line arguments passed to the underlying
    ``wkhtmltopdf`` binary.
    Default is controlled by :ref:`WKHTMLTOPDF-CMD-ARGS`.

    wkhtmltopdf options can be found by running ``wkhtmltopdf --help``.
    Unfortunately they don't provide hosted documentation.

.. note::

    For convenience in development you can add the GET arg ``?as=html`` to the
    end of your URL to render the PDF as a web page.

.. _Django class-based template view: https://docs.djangoproject.com/en/dev/ref/class-based-views/base/#templateview


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
        cmd_args = [
            '--margin-top', '3',
            '--quiet',
        ]


Templates
---------

:py:class:`PDFTemplateView` uses the standard Django templating
language to turn templated HTML into PDFs.

Remember, you must not hard-code
``{{ MEDIA_URL }}`` or ``{{ STATIC_URL }}`` in your templates.
By default,
Django has ``TEMPLATE_CONTEXT_PROCESSORS``
that provides these context variables.
Ensure that you have the following in your ``settings.py`:

.. code-block:: python

    TEMPLATE_CONTEXT_PROCESSORS = [
        # ...
        'django.core.context_processors.media',
        'django.core.context_processors.static',
        # ...
    ],

:py:class:`PDFTemplateView` substitutes those settings at render-time
with ``file://`` paths that point to
``settings.MEDIA_ROOT`` and ``settings.STATIC_ROOT`` respectively.
This will set the appropriate context variables
so that ``wkhtmltopdf`` can load them.

**Incorrect**:

.. code-block:: html

    <html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US">
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>My Report</title>
        <script type="text/javascript" src="/static/report.js"></script>     <!-- BAD -->
        <link rel="stylesheet" type="text/css" href="/static/report.css" />  <!-- BAD -->
      </head>
      <body>...</body>
    </html>

**Correct**:

.. code-block:: html

    <html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en-US">
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>My Report</title>
        <script type="text/javascript" src="{{ STATIC_URL }}report.js"></script>     <!-- Good! -->
        <link rel="stylesheet" type="text/css" href="{{ STATIC_URL }}report.css" />  <!-- Good! -->
      </head>
      <body>...</body>
    </html>



Overriding other settings
-------------------------

You may need to add additional overrides to support other Django apps.
For instance, django-compressor requires that ``settings.COMPRESS_URL``
matches your ``settings.STATIC_URL``.

To accommodate this, you can add additional settings to override:

.. code-block:: python

    from wkhtmltopdf.views import PDFTemplateResponse, PDFTemplateView


    class MyPDFResponse(PDFTemplateResponse):
        # Make COMPRESS_URL match STATIC_URL
        default_override_settings = PDFTemplateResponse.default_override_settings.copy()
        default_override_settings['COMPRESS_URL'] = default_override_settings['STATIC_URL']


    class MyPDFView(PDFTemplateView):
        response_class = MyPDFResponse

Then, use ``MyPDFView`` as the base class for your other PDF views.


Hardcoded paths
---------------

In some templates,
you may have URLs that have been hardcoded,
yet cannot use context variables.
This may happen when you use
third-party Django apps or templates
that ignore Django best-practises.

To workaround this problem,
you can try to manually replace the offending URLs:

.. code-block:: python

    import os
    import re

    from django.conf import settings

    from wkhtmltopdf.utils import pathname2fileurl
    from wkhtmltopdf.views import PDFTemplateResponse, PDFTemplateView


    class MyPDFResponse(PDFTemplateResponse):
        # Don't override any settings
        default_override_settings = {}

        # Override pre_render to replace the URLs
        def pre_render(self, content, template_name, context):
            def repl(match):
                # Replace match with the appropriate file URL
                url = match.group('url')
                if url.startswith(settings.STATIC_URL):
                    path = url.replace(settings.STATIC_URL, settings.STATIC_ROOT, 1)
                elif url.startswith(settings.MEDIA_URL):
                    path = url.replace(settings.MEDIA_URL, settings.MEDIA_ROOT, 1)
                # Add more replacements, if necessary...
                else:
                    return match.group(0)
                return match.group('begin') + pathname2fileurl(path) + match.group('end')

            # Match URL in an attribute
            content = re.sub(
                r'(?P<begin>=\s*(?P<quote>["\']))'  # Begins with =" or ='
                r'(?P<url>/.*?)'                    # URL
                r'(?P<end>(?P=quote))',             # Ends with matching quote
                repl, content
            )
            content = re.sub(
                r'(?P<begin>=\s*)'  # Begins with =
                r'(?P<url>/.*?)'    # URL
                r'(?P<end>[\s>]|$)',  # Ends with space or end of file
                repl, content
            )
            # Match CSS url()
            content = re.sub(
                r'(?P<begin>url\(\s*(?P<quote>["\']?))'  # Begins with url(
                r'(?P<url>/.*?)'                         # URL
                r'(?P<end>(?P=quote)\))',                # Ends with closing )
                repl, content
            )

            return content


    class MyPDFView(PDFTemplateView):
        response_class = MyPDFResponse

.. note::
    That this method is fragile and prone to break,
    because it relies on regular expressions
    to guess at the URLs to replace.

    **Do not rely on this in the long-term.**


Unicode characters
------------------

Templates containing UTF-8 characters should be supported. You will need to
ensure that you set the Content-Type in your template file for `wkhtmltopdf` to
interpret it properly.

.. code-block:: html

    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
