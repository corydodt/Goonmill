"""
Mercurial hooks for this repo
"""


def changegroupRestart(ui, repo, **kw):
    node = kw['node']
    import pdb; pdb.set_trace()

commitRestart = changegroupRestart
