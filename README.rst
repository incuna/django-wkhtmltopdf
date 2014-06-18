django-wkhtmltopdf
==================

.. image:: https://travis-ci.org/incuna/django-wkhtmltopdf.png
   :target: https://travis-ci.org/incuna/django-wkhtmltopdf


Converts html to PDF
--------------------

Provides a thin Django wrapper for the `wkhtmltopdf`_ binary.

.. _wkhtmltopdf: http://wkhtmltopdf.org/

Requirements
------------

Install the `wkhtmltopdf`_ binary.

This requires libfontconfig (on Ubuntu: ``sudo aptitude install libfontconfig``).

.. _wkhtmltopdf: http://wkhtmltopdf.org/downloads.html

Python 2.6+ through 3.4 is supported.


Installation
------------

Run ``pip install django-wkhtmltopdf``.

Add ``'wkhtmltopdf'`` to ``INSTALLED_APPS`` in your ``settings.py``.

By default it will execute the first ``wkhtmltopdf`` command found on your ``PATH``.

If you can't add wkhtmltopdf to your ``PATH``, you can set ``WKHTMLTOPDF_CMD`` to a
specific execuatable:

e.g.: in ``settings.py``::

    WKHTMLTOPDF_CMD = '/path/to/my/wkhtmltopdf'

or alternatively as env variable::

    export WKHTMLTOPDF_CMD=/path/to/my/wkhtmltopdf

You may also set
``WKHTMLTOPDF_CMD_OPTIONS``
in ``settings.py`` to a dictionary of default command-line options.

The default is::

    WKHTMLTOPDF_CMD_OPTIONS = {
        'quiet': True,
    }
