try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages
setup(name='Goonmill',
      version='0.2',
      author='Cory Dodt',
      description='Goonmill Monster Generator',
      url='http://goonmill.goonmill.org/',
      download_url='http://goonmill-source.goonmill.org/archive/tip.tar.gz',

      packages=find_packages(exclude=['goonmill.commonsgetter',
          'goonmill.hg',
          ]),

      install_requires=[
          'pysqlite>=2',
          'storm>=0.13',
          'playtools',
          'zope.interface',
          'twisted',
          'nevow',
          'simpleparse',
          'hypy',
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
