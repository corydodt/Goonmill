try:
    import setuptools
    setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages
setup(name='Goonmill',
      version='0.2.1',
      author='Cory Dodt',
      description='Goonmill Monster Generator',
      url='http://goonmill.goonmill.org/',
      download_url='http://goonmill-source.goonmill.org/archive/tip.tar.gz',

      packages=find_packages(exclude=['goonmill.commonsgetter',
          'goonmill.hg',
          ]),

      install_requires=[
          'playtools>=0.3.0',
          'nevow',
          ],

      package_data={
          'goonmill': [ 'sql/*.sql', 
              'templates/*',
              'static/*.png',
              'static/*.css',
              'static/*.js',
              'static/*.gif',
              'static/*.xhtml',
              'static/upload/README.txt',
              'static/Goonmill/*.js',
              'static/monster/*.png',
              'static/3p/*',
              ],
        },
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Games/Entertainment :: Role-Playing',
          ],

      )
