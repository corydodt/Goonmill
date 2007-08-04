"""Mercurial stuff

To use, add

[extensions]
goonmillext = /.../goonmill/hg/hooks.py

[hooks]
changegroup._0update = hg up
changegroup._1restart = goonmillext.changegroupRestart
commit = goonmillext.commitRestart

"""
