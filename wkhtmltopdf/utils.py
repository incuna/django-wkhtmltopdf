from __future__ import absolute_import

from copy import copy
from itertools import chain
from os import fdopen
import sys
from tempfile import mkstemp
import warnings

from django.conf import settings
from django.template import loader
from django.utils.encoding import smart_str

from .subprocess import check_output


def _options_to_args(**options):
    """Converts ``options`` into a string of command-line arguments."""
    flags = []
    for name in sorted(options):
        value = options[name]
        if value is None:
            continue
        flags.append('--' + name.replace('_', '-'))
        if value is not True:
            flags.append(unicode(value))
    return flags


def wkhtmltopdf(pages, output=None, **kwargs):
    """
    Converts html to PDF using http://code.google.com/p/wkhtmltopdf/.

    pages: List of file paths or URLs of the html to be converted.
    output: Optional output file path. If None, the output is returned.
    **kwargs: Passed to wkhtmltopdf via _extra_args() (See
              https://github.com/antialize/wkhtmltopdf/blob/master/README_WKHTMLTOPDF
              for acceptable args.)
              Kwargs is passed through as arguments. e.g.:
                  {'footer_html': 'http://example.com/foot.html'}
              becomes
                  '--footer-html http://example.com/foot.html'

              Where there is no value passed, use True. e.g.:
                  {'disable_javascript': True}
              becomes:
                  '--disable-javascript'

              To disable a default option, use None. e.g:
                  {'quiet': None'}
              becomes:
                  ''

    example usage:
        wkhtmltopdf(pages=['/tmp/example.html'],
                    dpi=300,
                    orientation='Landscape',
                    disable_javascript=True)
    """
    if isinstance(pages, basestring):
        # Support a single page.
        pages = [pages]

    if output is None:
        # Standard output.
        output = '-'

    # Default options:
    options = getattr(settings, 'WKHTMLTOPDF_CMD_OPTIONS', None)
    if options is None:
        options = {'quiet': True}
    else:
        options = copy(options)
    options.update(kwargs)

    cmd = getattr(settings, 'WKHTMLTOPDF_CMD', 'wkhtmltopdf')
    args = list(chain([cmd],
                      _options_to_args(**options),
                      list(pages),
                      [output]))
    return check_output(args, stderr=sys.stderr)


def template_to_temp_file(template_name, dictionary=None, context_instance=None):
    """
    Renders a template to a temp file, and returns the path of the file.
    """
    warnings.warn('template_to_temp_file is deprecated in favour of PDFResponse. It will be removed in version 1.',
                  PendingDeprecationWarning, 2)
    file_descriptor, tempfile_path = mkstemp(suffix='.html')
    with fdopen(file_descriptor, 'wt') as f:
        f.write(smart_str(loader.render_to_string(template_name, dictionary=dictionary, context_instance=context_instance)))
    return tempfile_path


def content_disposition_filename(filename):
    """
    Sanitize a file name to be used in the Content-Disposition HTTP
    header.

    Even if the standard is quite permissive in terms of
    characters, there are a lot of edge cases that are not supported by
    different browsers.

    See http://greenbytes.de/tech/tc2231/#attmultinstances for more details.
    """
    filename = filename.replace(';', '').replace('"', '')
    return http_quote(filename)


def http_quote(string):
    """
    Given a unicode string, will do its dandiest to give you back a
    valid ascii charset string you can use in, say, http headers and the
    like.
    """
    if isinstance(string, unicode):
        try:
            import unidecode
            string = unidecode.unidecode(string)
        except ImportError:
            string = string.encode('ascii', 'replace')
    # Wrap in double-quotes for ; , and the like
    return '"{!s}"'.format(string.replace('\\', '\\\\').replace('"', '\\"'))


try:
    # From Django 1.4
    from django.conf import override_settings
except ImportError:
    class override_settings(object):
        """
        Acts as either a decorator, or a context manager. If it's a decorator it
        takes a function and returns a wrapped function. If it's a contextmanager
        it's used with the ``with`` statement. In either event entering/exiting
        are called before and after, respectively, the function/block is executed.
        """
        def __init__(self, **kwargs):
            self.options = kwargs
            self.wrapped = settings._wrapped

        def __enter__(self):
            self.enable()

        def __exit__(self, exc_type, exc_value, traceback):
            self.disable()

        def __call__(self, test_func):
            from django.test import TransactionTestCase
            if isinstance(test_func, type) and issubclass(test_func, TransactionTestCase):
                original_pre_setup = test_func._pre_setup
                original_post_teardown = test_func._post_teardown
                def _pre_setup(innerself):
                    self.enable()
                    original_pre_setup(innerself)
                def _post_teardown(innerself):
                    original_post_teardown(innerself)
                    self.disable()
                test_func._pre_setup = _pre_setup
                test_func._post_teardown = _post_teardown
                return test_func
            else:
                @wraps(test_func)
                def inner(*args, **kwargs):
                    with self:
                        return test_func(*args, **kwargs)
            return inner

        def enable(self):
            override = copy(settings._wrapped)
            for key, new_value in self.options.items():
                setattr(override, key, new_value)
            settings._wrapped = override

        def disable(self):
            settings._wrapped = self.wrapped
