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

.. _downloads page: http://wkhtmltopdf.org/downloads.html

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
