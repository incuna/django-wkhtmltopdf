Full Installation Notes
=======================

Installing the Package
----------------------

From PyPI
~~~~~~~~~

.. code-block:: bash

    pip install django-wkhtmltopdf


From source
~~~~~~~~~~~

.. code-block:: bash

    git clone git://github.com/incuna/django-wkhtmltopdf.git
    cd django-wkhtmltopdf
    python setup.py install


Installing the Binary
---------------------

Find the relevant version of the ``wkhtmltopdf`` binary from the project
`downloads page`_.

You might need to install ``libfontconfig``.

You can alternatively install wkhtmltopdf from source via Homebrew or
apt-get/aptitude, but as this requires a full compilation of QT it's not
recommended.

.. note::

    The downloads page can be quite confusing. Make sure you get wkhtmltopdf
    (there are a few different libraries on there) and the correct platform.

.. note::

    There is an known issue on 64bit machines where ``wkhtmltopdf`` will fail
    silently. `This page`_ details ways to get around this but the easiest
    way to fix the issue is to install the 32bit binary.

.. _downloads page: http://code.google.com/p/wkhtmltopdf/downloads/list
.. _this page: http://code.google.com/p/wkhtmltopdf/wiki/static

Setting up your Django
----------------------

Add ``wkhtmltopdf`` to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        'wkhtmltopdf',
        # ...
    )

By default it will try to execute the ``wkhtmltopdf`` command from your ``PATH``.

If you can't add wkhtmltopdf to your ``PATH`` or you want to use some other
version, you can use the ``WKHTMLTOPDF_CMD`` setting:

.. code-block:: python

    WKHTMLTOPDF_CMD = '/path/to/my/wkhtmltopdf'
