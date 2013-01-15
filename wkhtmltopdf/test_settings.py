import os

DEBUG = True

DIRNAME = os.path.abspath(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MEDIA_ROOT = os.path.join(DIRNAME, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(DIRNAME, 'static')
STATIC_URL = '/static/'

INSTALLED_APPS = (
    'wkhtmltopdf.tests',
    'wkhtmltopdf',
)

TEMPLATE_DIRS = [
    os.path.join(DIRNAME, 'testproject', 'tests', 'templates'),
]

WKHTMLTOPDF_DEBUG = DEBUG
