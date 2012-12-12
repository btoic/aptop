import sys
assert sys.version >= '2' , 'Install Python 2.0 or greater'

from setuptools import setup, find_packages

# $Id: setup.py,v 1.2 2007/05/10 16:17:05 jay Exp $

def runSetup ():
    setup(name='aptop',
          version='0.2.1b',
          author='Branko Toic' ,
          author_email='branko@toic.org' ,
          url='https://bitbucket.org/btoic/aptop/get/master.tar.gz' ,
          license='GPLv2' ,
          install_requires=['lxml'],
          setup_requires=['lxml'],
          platforms=[ 'unix' ] ,
          description='ApTop is top like clone for apaache geting info from' \
              ' apache mod_status' ,
          packages=find_packages(),
          scripts=['aptop.py'],
          provides=['ApTop'],
    )

if __name__ == '__main__':
    runSetup()
