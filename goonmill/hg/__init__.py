"""Mercurial stuff

To use, add

[extensions]
goonmillext = /.../goonmill/hg/hooks.py

[hooks]
changegroup = hg up
changegroup = goonmillext.changegroupRestart
commit = goonmillext.commitRestart

"""
