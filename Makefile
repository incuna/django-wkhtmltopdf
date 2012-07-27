SHELL := /bin/bash

release:
	python setup.py register sdist upload

test:
	python wkhtmltopdf/_testproject/manage.py test wkhtmltopdf
