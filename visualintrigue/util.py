import re
import unicodedata
from werkzeug import secure_filename
import os
from visualintrigue import siteconfig
from datetime import datetime
import uuid
import boto3
import boto.s3.connection
import subprocess
import exifread
import json
import logging
import errno
import requests
import json

def getUrl(path):
    """ 
    Helper function that obtains the results for a given URL
    """
    resp = None
    params = {'key':'dkeiav38ganb72pa9a3ybvfg76425'}
    resp = requests.get(siteconfig.API + path,params=params)
    if resp.ok:
        return  json.loads(resp.content.decode('utf-8'))


def get_exif(path):
    """
    Extracts the EXIF information from the file
    """

    log = logging.getLogger("app")
    ret = {
        'fnumber':"unknown",
        'model':"unknown",
        'exposuremode':'unknown',
        'make': 'unknown',
        'exposureprogram': 'unknown',
        'focallength': 'unknown',
        'iso': 'unknwon',
        'aperture': 'unknown',
        'exposuretime':'unknown',
        'exposurebias':'unknown'
        }


    # Return Exif tags
    if os.path.exists(path):
        try:

            f = open(path, 'rb')
            exif = exifread.process_file(f)
            f.close()

            if 'EXIF ExposureBiasValue' in exif:
                ret['exposurebias'] = str(exif['EXIF ExposureBiasValue'])

            if 'Image Model' in exif:
                ret['model'] = str(exif['Image Model'])

            if 'EXIF ExposureMode' in exif:
                ret['exposuremode'] = str(exif['EXIF ExposureMode'])

            if 'Image Make' in exif:
                ret['make'] = str(exif['Image Make'])

            if 'EXIF ExposureProgram' in exif:
                ret['exposureprogram'] = str(exif['EXIF ExposureProgram'])

            if 'EXIF FocalLength' in exif:
                ret['focallength'] = str(exif['EXIF FocalLength'])

            if 'EXIF ISOSpeedRatings' in exif:
                ret['iso'] = str(exif['EXIF ISOSpeedRatings'])

            if 'EXIF ApertureValue' in exif:
                ret['aperture'] = str(exif['EXIF ApertureValue'])

            if 'EXIF ExposureTime' in exif:
                ret['exposuretime'] = str(exif['EXIF ExposureTime'])

            if 'EXIF FNumber' in exif:
                ret['fnumber'] = str(exif['EXIF FNumber'])


            for key in ret:
                log.info(ret[key])

            return ret

        except Exception as e:
            raise Exception("Could not read exif information from file %s with error %s"%(path,str(e)))
    else:
        raise Exception("Error could not find the %s for extracting exif information"%(path))

    return ret

def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def summary_text(text):
    replace = ['&nbsp;',]
    text = re.sub('<[^<]+?>', '', text)
    for r in replace:
        text = text.replace(r,'')
    ret = ""

    items = text.split()
    size = 65
    if len(items) < 65:
        size = len(items)
    for item in items[0:size]:
        ret = ret + " " + item.strip()
    if len(items) >= 65:
        ret = ret + "..."
    return ret

def main():
    pass


if __name__ == "__main__":
    main()

