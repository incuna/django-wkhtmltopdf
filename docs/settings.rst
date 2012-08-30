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

WKHTMLTOPDF_CMD_OPTIONS
~~~~~~~~~~~~~~~~~~~~~~~

Default: ``{'encoding': 'utf8', 'quiet': True}``

A dictionary of command-line arguments to pass to the ``wkhtmltopdf``
binary.
Keys are the name of the flag and values are arguments for the flag.

To pass a simple flag,
for example:
``wkhtmltopdf --disable-javascript``:

.. code-block:: python

    WKHTMLTOPDF_CMD_OPTIONS = {'disable-javascript': True}

To pass a flag with an argument,
for example:
``wkhtmltopdf --title 'TPS Report'``:

.. code-block:: python

    WKHTMLTOPDF_CMD_OPTIONS = {'title': 'TPS Report'}


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
