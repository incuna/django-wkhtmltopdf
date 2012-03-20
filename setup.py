from os.path import dirname, join
from setuptools import setup, find_packages

from wkhtmltopdf import get_version


def fread(fn):
    with open(join(dirname(__file__), fn), 'r') as f:
        return f.read()

setup(
    name = "django-wkhtmltopdf",
    packages = find_packages(),
    include_package_data=True,
    version = get_version(),
    description = "Converts html to PDF using http://code.google.com/p/wkhtmltopdf/.",
    long_description = fread('README.rst'),
    author = "Incuna Ltd",
    author_email = "admin@incuna.com",
    url = "http://incuna.com/",
)

