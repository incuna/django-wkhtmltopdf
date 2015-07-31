django-wkhtmltopdf
==================

.. image:: https://badge.fury.io/py/django-wkhtmltopdf.png
    :target: http://badge.fury.io/py/django-wkhtmltopdf
    :alt: Latest version

.. image:: https://travis-ci.org/incuna/django-wkhtmltopdf.png?branch=master
   :target: https://travis-ci.org/incuna/django-wkhtmltopdf
   :alt: Travis-CI

.. image:: https://pypip.in/d/django-wkhtmltopdf/badge.png
    :target: https://crate.io/packages/django-wkhtmltopdf/
    :alt: Number of PyPI downloads


Converts HTML to PDF
--------------------

Provides Django views to wrap the HTML to PDF conversion of the `wkhtmltopdf <http://wkhtmltopdf.org>`_ binary.

Requirements
------------

Install the `wkhtmltopdf static binary <http://wkhtmltopdf.org/downloads.html>`_.

This requires libfontconfig (on Ubuntu: ``sudo aptitude install libfontconfig``).

Python 2.6+ and 3.3+ are supported.


Installation
------------

Run ``pip install django-wkhtmltopdf``.

Add ``'wkhtmltopdf'`` to ``INSTALLED_APPS`` in your ``settings.py``.

By default it will execute the first ``wkhtmltopdf`` command found on your ``PATH``.

If you can't add wkhtmltopdf to your ``PATH``, you can set ``WKHTMLTOPDF_CMD`` to a
specific executable:

e.g. in ``settings.py``: ::

    WKHTMLTOPDF_CMD = '/path/to/my/wkhtmltopdf'

or alternatively as env variable: ::

    export WKHTMLTOPDF_CMD=/path/to/my/wkhtmltopdf

You may also set ``WKHTMLTOPDF_CMD_OPTIONS`` in ``settings.py`` to a dictionary
of default command-line options.

The default is: ::

    WKHTMLTOPDF_CMD_OPTIONS = {
        'quiet': True,
    }

Documentation
-------------

Documentation is available at http://django-wkhtmltopdf.readthedocs.org/en/latest/.

License
-------

MIT licensed. See the bundled `LICENSE <https://github.com/incuna/django-wkhtmltopdf/blob/master/LICENSE>`_ file for more details.
