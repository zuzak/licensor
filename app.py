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
import requests
import sys

ENDPOINT_LICENSES = 'https://api.opensource.org/licenses/'
ENDPOINT_TEXTS = 'https://raw.githubusercontent.com/OpenSourceOrg/licenses/master/texts/plain/'


def pull_licenses():
    data = requests.get(ENDPOINT_LICENSES)
    licenses = data.json()

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

    if 'discouraged' in license['keywords']:
        if not prompt_boolean(
            'Use of the {0} has been discouraged by the Open Source Initative.'
            ' Continue?'
            .format(license['name'])
        ):
            return 1

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
    else:
        print('No license text found')
        return 1


def get_license_text(license):
    texts = license['text']
    for text in texts:
        if text['media_type'] == 'text/plain':
            res = requests.get(text['url'])
            return res.text()

    # No nicely formatted license text
    url = ENDPOINT_TEXTS + license['id']
    res = requests.get(url)
    if res.status_code == 200:
        return res.text

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
