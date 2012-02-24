django-wkhtmltopdf
==================


Converts html to PDF
--------------------

Provides a thin wrapper to the wkhtmltopdf binary from http://code.google.com/p/wkhtmltopdf/


Requirements
------------

Install the [wkhtmltopdf](http://code.google.com/p/wkhtmltopdf/) binary.
This requires libfontconfig (on Ububtu: `sudo aptitude install libfontconfig`).


Installation
------------

Run `pip install django-wkhtmltopdf`.

Add `'wkhtmltopdf'` to `INSTALLED_APPS` in your `settings.py`.

By default it will execute the first wkhtmltopdf command found on your `PATH`.

If you can't add wkhtmltopdf to your `PATH`, you can set `WKHTMLTOPDF_CMD` to a
specific execuatable:

e.g.: in `settings.py`
    WKHTMLTOPDF_CMD = '/path/to/my/wkhtmltopdf'
