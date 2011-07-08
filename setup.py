from distutils.core import setup
setup(
    name = "wkhtmltopdf",
    packages = ["wkhtmltopdf", ],
    include_package_data=True,
    #install_requires=[],
    version = "0.1",
    description = "Converts html to PDF using http://code.google.com/p/wkhtmltopdf/.",
    author = "Incuna Ltd",
    author_email = "admin@incuna.com",
    url = "http://incuna.com/",
)
