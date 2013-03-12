Settings
========

Available settings
------------------

Here's a full list of available settings,
in alphabetical order,
and their default values.

WKHTMLTOPDF_CMD
~~~~~~~~~~~~~~~

Default: ``'wkhtmltopdf'``

The name of the ``wkhtmltopdf`` binary.

If there are no path components,
this app will look for the binary using the default OS paths.

.. _WKHTMLTOPDF-CMD-ARGS:

WKHTMLTOPDF_CMD_ARGS
~~~~~~~~~~~~~~~~~~~~

Default: ``['--encoding', 'utf8', '--quiet']``

A default list of command-line arguments
to pass to the ``wkhtmltopdf`` binary.

To pass a simple flag,
for example:
``wkhtmltopdf --disable-javascript``:

.. code-block:: python

    WKHTMLTOPDF_CMD_ARGS = ['--disable-javascript']

To pass a flag with an argument,
for example:
``wkhtmltopdf --title 'TPS Report'``:

.. code-block:: python

    WKHTMLTOPDF_CMD_ARGS = ['--title', 'TPS Report']

.. note::

    Since you may pass multiple options to ``wkhtmltopdf``,
    these default arguments are always passed in when it is run.
    If you want full control over the arguments used, make sure
    to pass in an empty list:

    .. code-block:: python

        WKHTMLTOPDF_CMD_ARGS = []


WKHTMLTOPDF_DEBUG
~~~~~~~~~~~~~~~~~

Default: same as :py:data:`settings.DEBUG`

A boolean that turns on/off debug mode.

WKHTMLTOPDF_ENV
~~~~~~~~~~~~~~~

Default: ``None``

An optional dictionary of environment variables to override,
when running the ``wkhtmltopdf`` binary.
Keys are the name of the environment variable.

A common use of this is to set the ``DISPLAY`` environment variable
to another X server,
when using ``wkhtmltopdf --use-xserver``:

.. code-block:: python

    WKHTMLTOPDF_ENV = {'DISPLAY': ':2'}
