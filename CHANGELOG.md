Changelog for django-wkhtmltopdf
================================

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
