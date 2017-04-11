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

Display static files
----------------------

Set ``STATIC_ROOT`` in your ``settings.py``:

.. code-block:: python

    STATIC_ROOT = '/full/path/to/static/directory/'
    
Make sure your static files and directories are inside this directory.

**Note:**
In production static files are supposed to reside outside the project folder, in a public directory. The STATIC_ROOT-setting gives the path to this directory. However, django-wkhtmltopdf requires that STATIC_ROOT is also set on your local machine. 

In development the static files reside in their respective apps folder or in a cross-app directory defined by the STATIC_DIRS-setting. Refer to the django documentation for how you can move static files to the STATIC_ROOT directory through a django script.

