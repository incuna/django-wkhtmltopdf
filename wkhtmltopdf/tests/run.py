#! /usr/bin/env python
import os
import sys

import django
from django.conf import settings

DIRNAME = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, os.getcwd())

settings.configure(
    DEBUG=False,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=(
        'django.contrib.contenttypes',
        'wkhtmltopdf.tests',
        'wkhtmltopdf',
    ),
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
    ),
    MEDIA_ROOT=os.path.join(DIRNAME, 'media'),
    MEDIA_URL='/media/',
    STATIC_ROOT=os.path.join(DIRNAME, 'static'),
    STATIC_URL='/static/',
    TEMPLATES = [  # For Django >= 1.10. Ignored in lower versions
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'DIRS': [],
            'OPTIONS': {},
        },
    ],
    WKHTMLTOPDF_DEBUG=False,
)

try:
    django.setup()
except AttributeError:
    pass  # Django < 1.7; okay to ignore


try:
    from django.test.runner import DiscoverRunner
except ImportError:
    from discover_runner.runner import DiscoverRunner


test_runner = DiscoverRunner(verbosity=1)
failures = test_runner.run_tests(['wkhtmltopdf'])
if failures:
    sys.exit(1)
