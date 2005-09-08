#!/usr/bin/env python

from distutils.core import setup
import py2exe
import sys

if len(sys.argv) == 1 :
    sys.argv += ['py2exe']

setup(
    name='pysvngraph',
    console=[
        {
            "script": "pysvngraph.py",
            "icon_resources": [(1,'../res/pysvngraph.ico')],
            },
        ],
    options={
        "py2exe" : {
            "includes" : ["encodings","encodings.latin_1",],
            "excludes": [],
            },
        },
)
