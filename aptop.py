#!/usr/bin/env python3

__author__ = "branko.toic@gmail.org (https://toic.org)"
__date__ = "Oct 17, 2023 0:10 PM$"
__version__ = "0.4.0"


from ApTop import ApacheStatus
from ApTop import AptopCurses


if __name__ == "__main__":
    aptop = ApacheStatus()
    window = AptopCurses(aptop)
