==================
django-wkhtmltopdf
==================

``django-wkhtmltopdf`` allows a Django site to output dynamic PDFs. It utilises
the wkhtmltopdf_ library, allowing you to write using the technologies you know
- HTML and CSS - and output a PDF file.

.. _wkhtmltopdf: http://wkhtmltopdf.org/

Quickstart
==========

.. code-block:: bash

    pip install django-wkhtmltopdf

Grab the wkhtmltopdf binary_ for your platform.

.. _binary: http://wkhtmltopdf.org/downloads.html

``settings.py``

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        'wkhtmltopdf',
        # ...
    )

``urls.py``

.. code-block:: python

    from django.conf.urls.defaults import url, patterns
    from wkhtmltopdf.views import PDFTemplateView

    urlpatterns = patterns('',
        url(r'^pdf/$', PDFTemplateView.as_view(template_name='my_template.html',
                                               filename='my_pdf.pdf'), name='pdf'),
    )

Contribute
==========

You can fork the project on Github_.

.. _Github: https://github.com/incuna/django-wkhtmltopdf

Contents
========

.. toctree::
    :maxdepth: 1

    installation
    usage
    settings
