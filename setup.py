import sys
assert sys.version >= '2' , 'Install Python 2.0 or greater'

from setuptools import setup

# $Id: setup.py,v 1.2 2007/05/10 16:17:05 jay Exp $

def runSetup ():
    setup(name='aptop',
          version='0.1.0',
          author='Branko Toic' ,
          author_email='branko@toic.org' ,
          url='http://toic.org' ,
          license='GPLv2' ,
          install_requires=['lxml'],
          platforms=[ 'unix' ] ,
          description='ApTop is top like clone for apaache geting info from' \
              ' apache mod_status' ,
          packages=['ApTop'] ,
          scripts=['aptop.py'],
          data_files=[('/etc', ['data/aptop.conf']), ],
    )

if __name__ == '__main__':
    runSetup()