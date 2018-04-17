#!/bin/bash

# Setup build environment for vi

set -e 

# Use PYTHON3

/usr/local/bin/virtualenv python

python/bin/pip install -r requirements.txt

python3/bin/python3 run.py



