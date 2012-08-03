SHELL := /bin/bash

release:
	python setup.py register sdist upload

test:
	django-admin.py test tests --settings=wkhtmltopdf.test_settings
