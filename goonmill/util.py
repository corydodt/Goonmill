import codecs

from twisted.python.util import sibpath

RESOURCE = lambda f: sibpath(__file__, f)

def resourceData(f, encoding='utf8'):
    return codecs.open(RESOURCE(f), 'r', encoding).read()
