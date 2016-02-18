#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hubzip.
A small script to automatically download/decompress master zips from Github.
"""


import os
import re
import sys


from argparse import ArgumentParser, RawDescriptionHelpFormatter
from contextlib import closing

from zipfile import ZipFile


# Information and error messages:

def outln(line):
    """ Write 'line' to stdout, using the platform encoding and newline format. """
    print(line, flush = True)


def errln(line):
    """ Write 'line' to stderr, using the platform encoding and newline format. """
    print('Hubzip.py: error:', line, file = sys.stderr, flush = True)


# Non-builtin imports:

try:
    import requests

except ImportError:
    errln('Hubzip requires the following modules:')
    errln('requests 2.9.1+ - <https://pypi.python.org/pypi/requests>')
    sys.exit(1)


# Downloading the zip:

GITHUB_URL_FORMAT = 'https://github.com/{username}/{repository}/archive/master.zip'
FILENAME_FORMAT = '{repository}-master.zip'

def download_github_zip(username, repository, chunk_size = 1024, quiet = False):
    """
    Downloads a repository zip from Github.
    Returns the resulting filename.
    """
    url = GITHUB_URL_FORMAT.format(username = username, repository = repository)

    with closing(requests.get(url, stream = True)) as response:
        response.raise_for_status()

        # validate headers:
        headers = response.headers

        content_type = headers.get('Content-Type')
        content_disposition = headers.get('Content-Disposition')
        content_length = headers.get('Content-Length')

        # type must be zip:
        if content_type != 'application/zip':
            raise ValueError('Invalid Content-Type: should be: "application/zip".')

        # guess filename or fall back to the default Github one:
        if content_disposition is not None:
            match = re.search('^(attachment; filename=)(.+)$', content_disposition)

            if match and match.lastindex == 2:
                filename = match.group(2)
            else:
                filename = FILENAME_FORMAT.format(repository = repository)

        # guess filesize or set to None:
        if content_length is not None:
            try:
                filesize = int(content_length)
            except ValueError:
                raise ValueError('Invalid Content-Length: not an int.')
        else:
            filesize = None

        # download:
        with open(filename, 'wb') as descriptor:
            for index, chunk in enumerate(response.iter_content(chunk_size), 1):
                descriptor.write(chunk)

                # print progress?
                if not quiet and filesize is not None:
                    downloaded = (chunk_size * index)

                    # the last chunk can overflow the filesize:
                    if downloaded > filesize:
                        downloaded = filesize

                    sys.stdout.write('\r {}: {:,} {:,} bytes.'.format(filename, downloaded, filesize))
                    sys.stdout.flush()

        # newline to separate messages:
        if not quiet:
            outln('')

        return filename


# Parser:

def make_parser():
    parser = ArgumentParser(
        description = __doc__,
        formatter_class = RawDescriptionHelpFormatter,
        epilog = 'example: Hubzip.py mitsuhiko/Flask',
        usage  = 'Hubzip.py username/repository [username/repository...] [option [options...]]',
    )

    # required:
    parser.add_argument('repositories',
        help = 'Github username/repository pairs to download and decompress',
        nargs = '+',
        type = str)

    # optional:
    parser.add_argument('--keep',
        help = 'keep the .zip files instead of deleting them',
        action = 'store_true')

    parser.add_argument('--quiet',
        help = 'do not print information/progress messages to stdout',
        action = 'store_true')

    return parser


# Entry point:

def main():
    parser = make_parser()
    options = parser.parse_args()

    for pair in options.repositories:

        if not '/' in pair:
            errln('Invalid username/repository combination.')
            sys.exit(1)

        username, repository = pair.split('/')
        username = username.strip()
        repository = repository.strip()

        if username == '':
            errln('Invalid or empty username.')
            sys.exit(1)

        if repository == '':
            errln('Invalid or empty repository.')
            sys.exit(1)

        # information:
        if not options.quiet:
           outln('{}/{}...'.format(username, repository))

        # download:
        try:
            filename = download_github_zip(username, repository, 1024, options.quiet)

        except Exception as err:
            errln('Unable to download: {}/{}.'.format(username, repository))
            errln('Exception message: {}'.format(err))
            sys.exit(1)

        # decompress:
        try:
            with ZipFile(filename, 'r') as descriptor:
                descriptor.extractall()

        except Exception as err:
            errln('Unable to decompress: {}.'.format(filename))
            errln('Exception message: {}'.format(err))
            sys.exit(1)

        # keep the zip itself?
        if not options.keep:
            try:
                os.remove(filename)

            except Exception as err:
                errln('Unable to remove: {}'.format(filename))
                errln('Exception message: {}'.format(err))
                sys.exit(1)

    # done:
    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

