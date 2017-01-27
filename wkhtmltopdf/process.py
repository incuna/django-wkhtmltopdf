import os
from subprocess import Popen, PIPE, STDOUT, CalledProcessError


def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the return code in the returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])  #doctest: +ELLIPSIS
    'crw-rw-rw-  1 root  wheel    3...

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=STDOUT.

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    'ls: non_existent_file: No such file or directory\n'

    Calling check_output without the ignore_404 keyword argument
    will raise a CalledProcessError if wkhtmltopdf exits with a non-zero code

    >>> check_output(['wkhtmltopdf',               #doctest: +ELLIPSIS
    ...               '--quiet',
    ...               '--encoding', 'utf8',
    ...               os.getenv('WKHTML_IN'), os.getenv('WKHTML_OUT')])
    Traceback (most recent call last):
    ...
    CalledProcessError...

    Calling check_output WITH the ignore_404 keyword will not raise
    the CalledProcessError, but only if the error == ContentNotFoundError

    >>> check_output(['/usr/local/bin/wkhtmltopdf',
    ...               '--quiet',
    ...               '--encoding', 'utf8',
    ...               os.getenv('WKHTML_IN'), os.getenv('WKHTML_OUT')],
    ...               env={'ignore_404': True})
    ''

    Calling check_output WITH the ignore_404 keyword should still
    raise a CalledProcessError if the error != ContentNotFoundError

    >>> check_output(['/usr/local/bin/wkhtmltopdf', #doctest: +ELLIPSIS
    ...               '--blaa',
    ...               '--encoding', 'utf8',
    ...               os.getenv('WKHTML_IN'), os.getenv('WKHTML_OUT')],
    ...               env={'ignore_404': True})
    Traceback (most recent call last):
    ...
    CalledProcessError...
    """
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')

    if 'env' in kwargs:
        ignore_404 = kwargs['env'].pop('ignore_404', False)
    else:
        ignore_404 = False

    if not kwargs.get('stderr'):
        kwargs['stderr'] = PIPE

    process = Popen(stdout=PIPE, *popenargs, **kwargs)
    output, error_message = process.communicate()
    retcode = process.poll()

    if retcode:
        if ignore_404:
            if 'ContentNotFoundError' in error_message:
                return output
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = CalledProcessError(retcode, cmd)
        # Add the output attribute to CalledProcessError, which
        # doesn't exist until Python 2.7.
        error.output = output
        raise error

    return output


if __name__ == "__main__":
    import doctest
    doctest.testmod()
