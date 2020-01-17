Changelog for django-wkhtmltopdf
================================

3.3.0
--------

* Fix `AttributeError` exception handling to only catch specific `AttributeError`.
* Fix list `NO_ARGUMENT_OPTIONS`.
* Add Django 3 support.
* Add Python 3.6, 3.7 and Django 2 to travis test matrix.
* Fix `make_absolute_paths` regular expression failure.

3.2.0
-----

* Adding support for cover page
* fix templates without context_processor
* Update installation docs
* Allow rendering PDFs when request is None
* Fix argument passing

3.1.0
-----

* Remove kwarg `current_app=None`.
* Fix download information badget on `README.rst`.
* Refactor to better support multiple pages.
* Remove dependency on Django template engine.
* Fix unidecode bytes error on python2.

3.0.0
-----

This release is identical to `2.1.0`, but with a major version bump to reflect the backwards-incompatible changes.

2.1.0
-----

This release is backwards-incompatible. Using `3.0.0` is recommended to indicate this.

* Move logic from views to `utils` to make it more usable. **backwards incompatible**
  - Adds `convert_to_pdf`, `render_pdf_from_template` and `render_to_temporary_file` to `utils`.
  - Removes `render_to_temporary_file` and `convert_to_pdf` from `views.PDFResponse` - thanks johnraz.
* Enable tests for Django >= 1.7 - thanks timb07
* Fix to accomodate changes to mod_wsgi v.4.4.14 - thanks powderflask
* Fix bytes string conversion issue - thanks danielgatis

2.0.3
--------

* Use shlex for argument splitting (thanks DeadWisdom)
* Skip absolute path substitution where STATIC or MEDIA URL are empty or None
  (thanks powderflask)

2.0.2
-----

* Fix Unicode encoding issues on Python2

2.0.1
-----

* Remove deprecated argument `mimetype` of `PDFResponse` class.

2.0.0
-----

* Support for Python 3
* Support other Django versions
* Use TestRunner for tests (and remove run_tests.sh)
* Add support for Wheel packaging
* Build the wkhtmltopdf binary in .travis.yml (and remove before_script.sh)

1.2.3
-----

* Update wkhtmltopdf binary to 0.12.0 version on before_script.sh
* Update docs to reference a wkhtmltopdf on github
* Add link to official site http://wkhtmltopdf.org/
* Move tests from Makefile to run_tests.sh


1.2.2
-----

* Fix tests on Travis due to its platform changes.
* Allow to define WKHTMLTOPDF_CMD as environment variable.


1.2.1
-----

* Test sys.stderr to ensure it hasn't been overridden.


1.2
---

* Fixed tests.
* Added option for not forcing download of PDF content. By default the content
  is saved to a file, but can be displayed in the browser directly when
  `show_content_in_browser` is set to True on `PDFTemplateView`.
* Removed duplicates when replacing STATIC/MEDIA paths.
* Fixed an issue when WKHTMLTOPDF_CMD consists of many parts.
* Fixed the local file paths so it works on Windows.


1.1
---

* Removed override_settings code for rewriting the STATIC and MEDIA URLs as it
  was not suitable for production use. It has been replaced with a string
  replace for just now, but a proper HTML parser may be required in the future.


1.0.1
-----

* Fixed a bug with unicode characters.


1.0
---

* Refactor of the PDFTemplateView to expose more options as class attributes.
* Addition/restructuring of several settings: `WKHTMLTOPDF_CMD`,
  `WKHTMLTOPDF_CMD_OPTIONS`, `WKHTMLTOPDF_DEBUG`, `WKHTMLTOPDF_ENV`.
* Reliable methods of passing command line arguments to the binary.
* Add compatibility by default with `staticfiles` and `django-compressor`.


0.3
---

* Fix a bug where temporary files were removed before the PDF was generated
  when using the header & footer options.
* Only set the `Content-Disposition` header in the response if `filename` is set.
* Added a Makefile for deployments.
* Added 2.6 requirement to the README.


0.2.2
-----

* Create a request context if one hasn't been passed into the view.


0.2.1
-----

* Use `get_template_names()` for extra extensibility.
* Be clear with `template_to_temp_file`'s arguments.


0.2
---

* Added option for orientation. Defaults to 'portrait', can be 'landscape'.
* Deprecated PdfTemplateView in preference of PDFTemplateView.
* Deprecated PdfResponse in preference of PDFResponse.
* Made PDFResponse more extensible.


0.1.1
-----
