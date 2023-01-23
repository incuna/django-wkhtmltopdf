from setuptools import setup, find_packages

import wkhtmltopdf


setup(
    name='django-wkhtmltopdf',
    packages=find_packages(),
    include_package_data=True,
    version=wkhtmltopdf.__version__,
    description='Converts HTML to PDF using wkhtmltopdf.',
    long_description=open('README.rst').read(),
    license='BSD-2-Clause',
    author=wkhtmltopdf.__author__,
    author_email='admin@incuna.com',
    url='https://github.com/incuna/django-wkhtmltopdf',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django',
    ],
    keywords='django wkhtmltopdf pdf',
    install_requires=[
        'six',
    ],
)
