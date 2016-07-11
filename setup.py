import io
import os
import re
import sys

from setuptools import setup, find_packages


def get_version_and_author(*file_paths):
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    with open(filename) as a_file:
        file_content = a_file.read()
        version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                                  file_content, re.M)
        author_match = re.search(r"^__author__ = ['\"]([^'\"]*)['\"]",
                                 file_content, re.M)
        if version_match and author_match:
            return version_match.group(1), author_match.group(1)
    raise RuntimeError('Unable to find version and/or author string.')


VERSION, AUTHOR = get_version_and_author('wkhtmltopdf', '__init__.py')

with io.open('README.rst', encoding='utf8') as readme_file:
    README = readme_file.read()  # NOQA

setup(
    name='django-wkhtmltopdf',
    packages=find_packages(),
    include_package_data=True,
    version=VERSION,
    description='Converts HTML to PDF using wkhtmltopdf.',
    long_description=README,
    license='MIT',
    author=AUTHOR,
    author_email='admin@incuna.com',
    url='https://github.com/incuna/django-wkhtmltopdf',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django',
    ],
    keywords='django wkhtmltopdf pdf',
)

