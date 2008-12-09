"""The classes that turn  L{Documentable} instances into objects Nevow can render."""

import os

from nevow import loaders

from pydoctor.nevowhtml.pages import CommonPage

def templatefile(filename):
    abspath = os.path.abspath(__file__)
    pydoctordir = os.path.dirname(os.path.dirname(os.path.dirname(abspath)))
    return os.path.join(pydoctordir, 'templates', filename)

class CommonPage(CommonPage):
    docFactory = loaders.xmlfile(templatefile('common.html'))
