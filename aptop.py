#!/usr/bin/env python

__author__ = "branko@toic.org (http://toic.org)"
__date__ = "Dec 24, 2012 0:10 PM$"
__version__ = "0.3.2b"


from ApTop import ApacheStatus
from ApTop import AptopCurses


if __name__ == "__main__":
    aptop = ApacheStatus()
    window = AptopCurses(aptop)
