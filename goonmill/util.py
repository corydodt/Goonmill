import codecs

from twisted.python.util import sibpath

RESOURCE = lambda f: sibpath(__file__, f) if f else None

def resourceData(f, encoding='utf8'):
    return codecs.open(RESOURCE(f), 'r', encoding).read()
