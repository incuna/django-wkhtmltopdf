Package
=======
PyPI
----

.. code-block:: bash

    pip install django-wkhtmltopdf


GitHub
------

.. code-block:: bash

    git clone git://github.com/incuna/django-wkhtmltopdf.git
    cd django-wkhtmltopdf
    python setup.py install


Binary
======

Find the relevant download link on the ``wkhtmltopdf`` project `downloads page`_.

This requires libfontconfig (on Ubuntu: ``sudo aptitude install libfontconfig``).

.. _downloads page: http://code.google.com/p/wkhtmltopdf/downloads/list

.. note::

    The wkhtmltopdf downloads page can be quite confusing. Make sure you get
    wkhtmltopdf (there are a few different libraries on there) and the correct platform.


.. note::

    At the time of writing it was possible to install wkhtmltopdf from Homebrew
    and apt-get/aptitude but required compilation of QT which can take quite a
    while so the binary installation is recommended.


.. note::

    There is an known issue on 64bit machines where wkhtmltopdf will fail
    silently. `This page`_ details ways to get around this but the easiest
    way to fix the issue is to install the 32bit binary.

.. _this page: http://code.google.com/p/wkhtmltopdf/wiki/static

Django
======

Add ``wkhtmltopdf`` to your ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = (
        # ...
        'wkhtmltopdf',
        # ...
    )

By default it will execute the first wkhtmltopdf command found on your ``PATH``.

If you can't add wkhtmltopdf to your ``PATH``, you can set ``WKHTMLTOPDF_CMD`` to a specific execuatable:

e.g.: in ``settings.py``

.. code-block:: python

    WKHTMLTOPDF_CMD = '/path/to/my/wkhtmltopdf'

