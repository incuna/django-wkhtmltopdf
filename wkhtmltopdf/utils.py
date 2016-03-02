from __future__ import absolute_import

from copy import copy
from itertools import chain
import os
import re
import sys
import shlex
from tempfile import NamedTemporaryFile

from django.utils.encoding import smart_text

try:
    from urllib.request import pathname2url
    from urllib.parse import urljoin
except ImportError:  # Python2
    from urllib import pathname2url
    from urlparse import urljoin

import django
from django.conf import settings
from django.template.context import Context, RequestContext
from django.utils import six

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
            flags.append(six.text_type(value))
    return flags


def wkhtmltopdf(pages, output=None, **kwargs):
    """
    Converts html to PDF using http://wkhtmltopdf.org/.

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
    if isinstance(pages, six.string_types):
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

    cmd = 'WKHTMLTOPDF_CMD'
    cmd = getattr(settings, cmd, os.environ.get(cmd, 'wkhtmltopdf'))

    ck_args = list(chain(shlex.split(cmd),
                         _options_to_args(**options),
                         list(pages),
                         [output]))
    ck_kwargs = {'env': env}
    # Handling of fileno() attr. based on https://github.com/GrahamDumpleton/mod_wsgi/issues/85
    try:
        i = sys.stderr.fileno()
        ck_kwargs['stderr'] = sys.stderr
    except (AttributeError, IOError):
        # can't call fileno() on mod_wsgi stderr object
        pass

    return check_output(ck_args, **ck_kwargs)

def convert_to_pdf(filename, header_filename=None, footer_filename=None, cmd_options=None):
    # Clobber header_html and footer_html only if filenames are
    # provided. These keys may be in self.cmd_options as hardcoded
    # static files.
    # The argument `filename` may be a string or a list. However, wkhtmltopdf
    # will coerce it into a list if a string is passed.
    cmd_options = cmd_options if cmd_options else {}

    if header_filename is not None:
        cmd_options['header_html'] = header_filename
    if footer_filename is not None:
        cmd_options['footer_html'] = footer_filename
    return wkhtmltopdf(pages=filename, **cmd_options)

class RenderedFile(object):
    """
    Create a temporary file resource of the rendered template with context.
    The filename will be used for later conversion to PDF.
    """
    temporary_file = None
    filename = ''

    def __init__(self, template, context, request=None):
        debug = getattr(settings, 'WKHTMLTOPDF_DEBUG', settings.DEBUG)

        self.temporary_file = render_to_temporary_file(
            template=template,
            context=context,
            request=request,
            prefix='wkhtmltopdf', suffix='.html',
            delete=(not debug)
        )
        self.filename = self.temporary_file.name

    def __del__(self):
        # Always close the temporary_file on object destruction.
        if self.temporary_file is not None:
            self.temporary_file.close()

def render_pdf_from_template(input_template, header_template, footer_template, context, request=None, cmd_options=None):
    # For basic usage. Performs all the actions necessary to create a single
    # page PDF from a single template and context.
    cmd_options = cmd_options if cmd_options else {}

    header_filename = footer_filename = None

    # Main content.
    input_file = RenderedFile(
        template=input_template,
        context=context,
        request=request
    )

    # Optional. For header template argument.
    if header_template:
        header_file = RenderedFile(
            template=header_template,
            context=context,
            request=request
        )
        header_filename = header_file.filename

    # Optional. For footer template argument.
    if footer_template:
        footer_file = RenderedFile(
            template=footer_template,
            context=context,
            request=request
        )
        footer_filename = footer_file.filename

    return convert_to_pdf(filename=input_file.filename,
                          header_filename=header_filename,
                          footer_filename=footer_filename,
                          cmd_options=cmd_options)

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
    if isinstance(string, six.text_type):
        try:
            import unidecode
        except ImportError:
            pass
        else:
            string = unidecode.unidecode(string)
        string = string.encode('ascii', 'replace')
    # Wrap in double-quotes for ; , and the like
    string = string.replace(b'\\', b'\\\\').replace(b'"', b'\\"')
    return '"{0!s}"'.format(string.decode())


def pathname2fileurl(pathname):
    """Returns a file:// URL for pathname. Handles OS-specific conversions."""
    return urljoin('file:', pathname2url(pathname))


def make_absolute_paths(content):
    """Convert all MEDIA files into a file://URL paths in order to
    correctly get it displayed in PDFs."""
    overrides = [
        {
            'root': settings.MEDIA_ROOT,
            'url': settings.MEDIA_URL,
        },
        {
            'root': settings.STATIC_ROOT,
            'url': settings.STATIC_URL,
        }
    ]
    has_scheme = re.compile(r'^[^:/]+://')

    for x in overrides:
        if not x['url'] or has_scheme.match(x['url']):
            continue

        if not x['root'].endswith('/'):
            x['root'] += '/'

        occur_pattern = '''["|']({0}.*?)["|']'''
        occurences = re.findall(occur_pattern.format(x['url']), content)
        occurences = list(set(occurences))  # Remove dups
        for occur in occurences:
            content = content.replace(occur,
                                      pathname2fileurl(x['root']) +
                                      occur[len(x['url']):])

    return content

def render_to_temporary_file(template, context, request=None, mode='w+b',
                             bufsize=-1, suffix='.html', prefix='tmp',
                             dir=None, delete=True):
    if django.VERSION < (1, 8):
        # If using a version of Django prior to 1.8, ensure ``context`` is an
        # instance of ``Context``
        if not isinstance(context, Context):
            if request:
                context = RequestContext(request, context)
            else:
                context = Context(context)
        content = template.render(context)
    else:
        content = template.render(context, request)

    content = smart_text(content)
    content = make_absolute_paths(content)

    try:
        # Python3 has 'buffering' arg instead of 'bufsize'
        tempfile = NamedTemporaryFile(mode=mode, buffering=bufsize,
                                      suffix=suffix, prefix=prefix,
                                      dir=dir, delete=delete)
    except TypeError:
        tempfile = NamedTemporaryFile(mode=mode, bufsize=bufsize,
                                      suffix=suffix, prefix=prefix,
                                      dir=dir, delete=delete)

    try:
        tempfile.write(content.encode('utf-8'))
        tempfile.flush()
        return tempfile
    except:
        # Clean-up tempfile if an Exception is raised.
        tempfile.close()
        raise
