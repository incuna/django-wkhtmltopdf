from __future__ import absolute_import

from copy import copy
from functools import wraps
from itertools import chain
import os
import sys
import urllib
from urlparse import urljoin

from django.conf import settings

from .subprocess import check_output


def _options_to_args(**options):
    """Converts ``options`` into a list of command-line arguments."""
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

    # Force --encoding utf8 unless the user has explicitly overridden this.
    options.setdefault('encoding', 'utf8')

    env = getattr(settings, 'WKHTMLTOPDF_ENV', None)
    if env is not None:
        env = dict(os.environ, **env)

    cmd = getattr(settings, 'WKHTMLTOPDF_CMD', 'wkhtmltopdf')
    args = list(chain(cmd.split(),
                      _options_to_args(**options),
                      list(pages),
                      [output]))
    return check_output(args, stderr=sys.stderr, env=env)


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
    return '"{0!s}"'.format(string.replace('\\', '\\\\').replace('"', '\\"'))


def pathname2fileurl(pathname):
    """Returns a file:// URL for pathname. Handles OS-specific conversions."""
    return urljoin('file:', urllib.pathname2url(pathname))
