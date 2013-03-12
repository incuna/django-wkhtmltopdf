django-wkhtmltopdf
==================

.. image:: https://travis-ci.org/incuna/django-wkhtmltopdf.png
   :target: https://travis-ci.org/incuna/django-wkhtmltopdf


Converts html to PDF
--------------------

Provides a thin wrapper to the wkhtmltopdf binary from http://code.google.com/p/wkhtmltopdf/


Requirements
------------

Install the `wkhtmltopdf`_ binary.
This requires libfontconfig (on Ubuntu: ``sudo aptitude install libfontconfig``).

.. _wkhtmltopdf: http://code.google.com/p/wkhtmltopdf/downloads/list

Python 2.6


Installation
------------

Run ``pip install django-wkhtmltopdf``.

Add ``'wkhtmltopdf'`` to ``INSTALLED_APPS`` in your ``settings.py``.

By default it will execute the first wkhtmltopdf command found on your ``PATH``.

If you can't add wkhtmltopdf to your ``PATH``, you can set ``WKHTMLTOPDF_CMD`` to a
specific execuatable:

e.g.: in ``settings.py``::

    WKHTMLTOPDF_CMD = '/path/to/my/wkhtmltopdf'

You may also set
``WKHTMLTOPDF_CMD_ARGS``
in ``settings.py`` to a list of default command-line options.

The default is::

    WKHTMLTOPDF_CMD_ARGS = [
        '--encoding', 'utf8',
        '--quiet',
    ]
