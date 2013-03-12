SHELL := /bin/bash

release:
	python setup.py register sdist upload

test:
	PYTHONPATH=.:$$PYTHONPATH; \
	    export PYTHONPATH; \
	    django-admin.py test tests --settings=wkhtmltopdf.test_settings
