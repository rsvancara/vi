#!/bin/bash

# Setup build environment for vi

set -e 

# Use PYTHON3

/usr/local/bin/virtualenv python

python/bin/python3 python/bin/pip3 install -r requirements.txt

python/bin/python3 run.py


