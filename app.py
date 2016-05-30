#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Douglas Gardner <douglas@chippy.ch>
#
# Distributed under terms of the MIT license.

"""
Speeds up adding a licence to new software projects.
"""

import json
import urllib

ENDPOINT_LICENSES = 'https://api.opensource.org/licenses/'


def pull_licenses():
    res = urllib.urlopen(ENDPOINT_LICENSES)
    licenses = json.loads(res.read())

    return {x['id']: x for x in licenses}

if __name__ == '__main__':
    print(pull_licenses())


