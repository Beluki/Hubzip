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
    errln('requests 2.7.0+ - <https://pypi.python.org/pypi/requests>')
    sys.exit(1)


# Downloading the zip:

GITHUB_URL_FORMAT = 'https://github.com/{username}/{repository}/archive/master.zip'
FILENAME_FORMAT = '{repository}-master.zip'

def download_github_zip(username, repository, chunk_size = 1024):
    """
    Downloads a repository zip from Github.
    Returns the resulting filename.
    """
    url = GITHUB_URL_FORMAT.format(username = username, repository = repository)

    with closing(requests.get(url, stream = True)) as response:
        response.raise_for_status()

        # validate headers:
        headers = response.headers

        # zip?
        if headers.get('Content-Type') != 'application/zip':
            raise ValueError('Invalid Content-Type: should be: application/zip.')

        # filename?
        # (or fallback to the default Github one)
        disposition = headers.get('Content-Disposition')

        if disposition is not None:
            header, filename = re.search('^(attachment; filename)=(.+)$', disposition).groups()
        else:
            filename = FILENAME_FORMAT.format(repository = repository)

        # download:
        with open(filename, 'wb') as descriptor:
            for chunk in response.iter_content(chunk_size):
                descriptor.write(chunk)

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
        help = 'do not print information messages to stdout',
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
            filename = download_github_zip(username, repository)

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

