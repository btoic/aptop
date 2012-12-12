#!/usr/bin/env python

__author__ = "branko@toic.org (http://toic.org)"
__date__ = "Dec 9, 2012 2:00 PM$"
__version__ = "0.2.1b"


from ApTop import ApacheStatus
from ApTop import AptopCurses


if __name__ == "__main__":
    aptop = ApacheStatus()
    window = AptopCurses(aptop)
