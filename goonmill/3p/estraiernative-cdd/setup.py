#
from setuptools import setup, Extension

ext = Extension("_estraiernative",
                ["estraiernative.c"],
                libraries=["estraier"],
                include_dirs=["/usr/include/estraier", "/usr/include/qdbm"],
                )

setup(
        name="Hypy", 
        description='Pythonic wrapper for Hyper Estraier',
        author='Yusuke YOSHIDA',
        author_email='usk@nrgate.jp',
        maintainer='Cory Dodt',
        maintainer_email='pypi@spam.goonmill.org',
        url='http://goonmill.org/hypy/',
        download_url='http://hypy-source.goonmill.org/archive/tip.tar.gz',
        version="0.2.1", 
        ext_modules=[ext],
        py_modules=['hypy'],

        classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries',
          'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
          ],
      )
