import sys

assert sys.version >= "3", "Install Python 3.0 or greater"

from setuptools import setup, find_packages

# $Id: setup.py,v 1.2 2007/05/10 16:17:05 jay Exp $


def runSetup():
    setup(
        name="aptop",
        version="0.4.0",
        author="Branko Toic",
        author_email="branko.toic@gmail.com",
        url="https://github.com/btoic/aptop",
        license="GPLv2",
        install_requires=["lxml"],
        setup_requires=["lxml"],
        platforms=["unix"],
        description="ApTop is top like clone for Apache",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        packages=find_packages(),
        scripts=["aptop.py"],
        provides=["ApTop"],
    )


if __name__ == "__main__":
    runSetup()
