#!/usr/bin/env bash

export WKHTMLTOPDF_CMD=`pwd`/wkhtmltox_folder/wkhtmltox/bin/wkhtmltopdf;
export PYTHONPATH=.:$$PYTHONPATH;

django-admin.py test tests --settings=wkhtmltopdf.test_settings
