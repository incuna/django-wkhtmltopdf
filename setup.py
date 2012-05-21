from setuptools import setup, find_packages

import wkhtmltopdf


setup(
    name='django-wkhtmltopdf',
    packages=find_packages(),
    include_package_data=True,
    version=wkhtmltopdf.__version__,
    description='Converts html to PDF using http://code.google.com/p/wkhtmltopdf/.',
    long_description=open('README.rst').read(),
    author=wkhtmltopdf.__author__,
    author_email='admin@incuna.com',
    url='http://incuna.com/',
)

