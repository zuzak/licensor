#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright © 2016 Douglas Gardner <douglas@chippy.ch>
#
# Distributed under terms of the MIT license.

"""
Speeds up adding a license to new software projects.
"""

from distutils.util import strtobool
from datetime import datetime

import argparse
import os
import pwd
import requests
import sys

ENDPOINT_LICENSES = 'https://api.opensource.org/licenses/'
ENDPOINT_TEXTS = 'https://raw.githubusercontent.com/OpenSourceOrg/licenses/master/texts/plain/'


def pull_licenses():
    data = requests.get(ENDPOINT_LICENSES)
    licenses = data.json()

    return {x['id']: x for x in licenses}


def get_license(name, args):
    licenses = pull_licenses()
    try:
        license = licenses[name]
    except KeyError:
        print('The license you asked for couldn\'t be found.')
        print('Specify it via its identifer, such as one of the following:')
        print()
        print_popular_licenses(licenses)
        print()
        print('For an exhaustive list of licenses and their identifiers,')
        print('see https://opensource.org/licenses')

        return 1

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

        if os.path.isfile(filename) and not args.clobber:
            print('{0} already exists; shan\'t clobber'.format(filename))
            return 1

        text = replace_placeholders(text)
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
            return res.text

    # No nicely formatted license text
    url = ENDPOINT_TEXTS + license['id']
    res = requests.get(url)
    if res.status_code == 200:
        return res.text

    return None


def replace_placeholders(text):
    # There are many placeholders used within OSI licenses
    # and none of them are standard, so this is just a
    # small selection to cover some of the more popular ones
    placeholders = {
        '<YEAR>': str(datetime.now().year),
        '<OWNER>': get_real_name(),
        '<COPYRIGHT HOLDER>': get_real_name()
    }
    old = text

    for key in placeholders:
        text = text.replace(key, placeholders[key])

    if old != text:
        print('Rewrote license to contain your details')
    return text


def prompt_boolean(question):
    return strtobool(input('{0} [y/n]: '.format(question)))


def print_popular_licenses(licenses):
    popular = []
    tab = 0
    for license in licenses:
        license = licenses[license]
        if 'popular' in license['keywords']:
            popular.append([license['id'], license['name']])
            if len(license['id']) > tab:
                tab = len(license['id'])

    for entry in popular:
        print('{0} ({1})'.format(
            entry[0].ljust(tab),
            entry[1]
        ))

    return popular


def get_real_name():
    return pwd.getpwuid(os.getuid())[4]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('license', metavar='NAME', help='the license to add')
    parser.add_argument('--clobber', help='overwrite an existing license file')
    parser.add_argument(
        '--file',
        metavar='FILE',
        help='where to write the license'
    )
    args = parser.parse_args()

    sys.exit(get_license(args.license, args))
