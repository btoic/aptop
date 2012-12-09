#!/usr/bin/env python

from ApTop import ApacheStatus

a = ApacheStatus()
if a.verify_mod_status():
    a.fetch_status()
    header_data = a.parse_header()
    hcount = 0
    for header_line in header_data:
        print "%s - %s" % (hcount, header_line.replace('\n', ''))
        hcount += 1
