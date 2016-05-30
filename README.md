# licensor
[![Build Status](https://travis-ci.org/zuzak/licensor.svg?branch=master)](https://travis-ci.org/zuzak/licensor)

Tool to pull a licence from the OSI website and into your new software project.

Every new software project should have a license attached to it, but it's sometimes
a faff. This tool makes it a little easier, by pulling the license you request
into the repository for you.

## Usage
```
$ app.py [LICENSE]
```

For example:
```
$ app.py LGPL-3.0
$ app.py MIT
$ app.py GPL-2.0 --clobber
```
