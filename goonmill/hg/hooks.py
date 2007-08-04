"""
Mercurial hooks for this repo
"""

from mercurial.node import bin

import os

def changegroupRestart(ui, repo, **kw):
    import pdb; pdb.set_trace()
    node = bin(kw['node'])
    os.system("make goonmill-stop")
    os.system("make goonmill-start")

commitRestart = changegroupRestart
