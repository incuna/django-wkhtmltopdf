#! /usr/bin/env python
import os
import sys

from colour_runner.django_runner import ColourRunnerMixin
from django.conf import settings

DIRNAME = os.path.abspath(os.path.dirname(__file__))


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
    MEDIA_ROOT=os.path.join(DIRNAME, 'media'),
    MEDIA_URL='/media/',
    STATIC_ROOT=os.path.join(DIRNAME, 'static'),
    STATIC_URL='/static/',
    WKHTMLTOPDF_DEBUG=True,
)

try:
    from django.test.runner import DiscoverRunner
except ImportError:
    from discover_runner.runner import DiscoverRunner


class TestRunner(ColourRunnerMixin, DiscoverRunner):
    pass


test_runner = TestRunner(verbosity=1)
failures = test_runner.run_tests(['wkhtmltopdf'])
if failures:
    sys.exit(1)
