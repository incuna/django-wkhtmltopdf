from setuptools import setup, find_packages

from wkhtmltopdf import get_version
setup(
    name = "django-wkhtmltopdf",
    packages = find_packages(),
    include_package_data=True,
    #install_requires=[],
    version = get_version(),
    description = "Converts html to PDF using http://code.google.com/p/wkhtmltopdf/.",
    author = "Incuna Ltd",
    author_email = "admin@incuna.com",
    url = "http://incuna.com/",
)
