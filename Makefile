SHELL := /bin/bash

release:
	python setup.py register sdist upload

test:
	python testproject/manage.py test wkhtmltopdf
