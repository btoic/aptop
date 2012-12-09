#!/usr/bin/env python

from ApTop import ApacheStatus

a = ApacheStatus()
if a.verify_mod_status():
    a.fetch_status()
    vhosts_data = a.parse_vhosts()
    vcount = 0
    for vhost_line in vhosts_data:
        print vhost_line
        vcount += 1
