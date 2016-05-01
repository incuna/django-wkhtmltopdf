import re
import ast
from setuptools import setup, find_packages


_version_re = re.compile(r'__version__\s+=\s+(.*)')
_author_re = re.compile(r'__author__\s+=\s+(.*)')

with open('wkhtmltopdf/__init__.py', 'rb') as f:
    content = f.read().decode('utf-8')
    version = str(ast.literal_eval(_version_re.search(
        content).group(1)))
    author = str(ast.literal_eval(_author_re.search(
        content).group(1)))


setup(
    name='django-wkhtmltopdf',
    packages=find_packages(),
    include_package_data=True,
    version=version,
    description='Converts HTML to PDF using wkhtmltopdf.',
    long_description=open('README.rst').read(),
    license='MIT',
    author=author,
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
