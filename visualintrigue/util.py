from visualintrigue import siteconfig
import logging
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

