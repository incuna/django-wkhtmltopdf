Converts html to PDF
====================

Provides a thin wrapper to the wkhtmltopdf binary from http://code.google.com/p/wkhtmltopdf/

REQUIREMENTS
============

Install the binary http://code.google.com/p/wkhtmltopdf/
    This may require libfontconfig (on Ububtu: sudo aptitude install libfontconfig)

INSTALLATION
============

Add 'wkhtmltopdf' to INSTALLED_APPS.

By default it will execute the first wkhtmltopdf command found on your PATH. 
You can set WKHTMLTOPDF_CMD to a specific execuatable:

e.g.
    WKHTMLTOPDF_CMD = '/path/to/my/wkhtmltopdf'
