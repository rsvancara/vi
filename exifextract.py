#!/usr/bin/env python

import sys
import argparse
import os
import exifread
import json

parser = argparse.ArgumentParser(description='Extract EXIF information from a file')
parser.add_argument('--file',help='File you want to process')
args = parser.parse_args()

print("Have file %s"%(args.file))

if os.path.exists(args.file):
    print("Opening file for reading")
    # Open image file for reading (binary mode)
    f = open(args.file, 'rb')

    # Return Exif tags
    tags = exifread.process_file(f)
    
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            print("Key: %s = %s" % (tag, tags[tag]))
