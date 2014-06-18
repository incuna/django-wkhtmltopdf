from setuptools import setup, find_packages

import wkhtmltopdf


setup(
    name='django-wkhtmltopdf',
    packages=find_packages(),
    include_package_data=True,
    version=wkhtmltopdf.__version__,
    description='Converts HTML to PDF using wkhtmltopdf.',
    long_description=open('README.rst').read(),
    license='MIT',
    author=wkhtmltopdf.__author__,
    author_email='admin@incuna.com',
    url='https://github.com/incuna/django-wkhtmltopdf',
    install_requires=['Django>=1.4'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='django wkhtmltopdf pdf',
)
