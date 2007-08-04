"""
Mercurial hooks for this repo
"""

from mercurial.node import bin

import os

def commitRestart(ui, repo, **kw):
    node = bin(kw['node'])
    os.chdir(repo.path + '/..')
    os.system("make goonmill-stop")
    os.system("make goonmill-start")

changegroupRestart = commitRestart
