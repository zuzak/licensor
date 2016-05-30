#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Douglas Gardner <douglas@chippy.ch>
#
# Distributed under terms of the MIT license.

"""
Speeds up adding a license to new software projects.
"""

from distutils.util import strtobool

import argparse
import json
import sys
from urllib.request import urlopen

ENDPOINT_LICENSES = 'https://api.opensource.org/licenses/'


def pull_licenses():
    res = urlopen(ENDPOINT_LICENSES)
    with urlopen(ENDPOINT_LICENSES) as res:
        licenses = json.loads(res.read().decode())

    return {x['id']: x for x in licenses}


def get_license(name, args):
    try:
        license = pull_licenses()[name]
    except KeyError:
        sys.exit('Error: license not found!')

    if license['superseded_by']:
        if prompt_boolean('{0} has been superseded by {1}. Use that instead?'
           .format(
                license['name'],
                license['superseded_by']
           )
        ):
            return get_license(license['superseded_by'])

    text = get_license_text(license)
    if text:
        filename = args.file
        if not filename:
            if 'copyleft' in license['keywords']:
                filename = 'COPYING'
            else:
                filename = 'LICENSE'

        with open(filename, 'w') as f:
            f.write(text)
            print('Wrote contents of {0} to {1}.'.format(
                license['name'],
                filename
            ))
            return 0


def get_license_text(license):
    texts = license['text']
    for text in texts:
        if text['media_type'] == 'text/plain':
            res = urlopen(text['url'])
            return res.read().decode()

    return None


def prompt_boolean(question):
    return strtobool(input('{0} [y/n]: '.format(question)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('license', metavar='NAME', help='the license to add')
    parser.add_argument(
        '--file',
        metavar='FILE',
        help='where to write the license'
    )
    args = parser.parse_args()

    sys.exit(get_license(args.license, args))
