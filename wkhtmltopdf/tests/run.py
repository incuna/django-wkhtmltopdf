#! /usr/bin/env python
import os
import sys

import django
from django.conf import settings

DIRNAME = os.path.abspath(os.path.dirname(__file__))

sys.path.insert(0, os.getcwd())

def run_tests():
    # Utility function to executes tests.
    # Will be called twice. Once with DEBUG=True and once with DEBUG=False.
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

settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    INSTALLED_APPS=(
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
    WKHTMLTOPDF_DEBUG=True,
)

# Run tests with True debug settings (persistent temporary files).
run_tests()

settings.DEBUG = False
settings.WKHTMLTOPDF_DEBUG = False

# Run tests with False debug settings to test temporary file delete operations.
run_tests()
