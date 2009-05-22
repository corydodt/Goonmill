from twisted.python.util import sibpath

RESOURCE = lambda f: sibpath(__file__, f) if f else None
