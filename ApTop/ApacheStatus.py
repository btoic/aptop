__author__ = "branko@toic.org (http://toic.org)"
__date__ = "Dec 9, 2012 2:00 PM$"
__version__ = "0.2.1b"

import ConfigParser
import os
import sys
from operator import itemgetter


"""
Now lets import some dependencies and check their versions
We need at least version 3.0.7a of BeautifulSoup
"""
try:
    import lxml.html #@UnresolvedImport
except:
    print "No lxml package found..."
    print "please install lxml >= 3.x.x"
    print "best way to install easy_install lxml"
    sys.exit(1)

class ApacheStatus(object):
    def __init__(self):
        """
        Try to detect config file location, trying to use user defined config
        in home path ~/.aptop.conf or /etc/aptop.conf then
        """
        homedir = os.path.expanduser('~')

        if os.path.isfile(os.path.join(homedir, '.aptop.conf')):
            self.configfile = os.path.join(homedir, '.aptop.conf')
        else:
            self.configfile = None

        """ 
        Let's populate some defaults if no config file is found
        """
        if not self.configfile:
            if os.path.isdir('/var/cpanel'):
                self.status_url = 'http://localhost/whm-server-status'
            else:
                self.status_url = 'http://localhost/server-status'
            self.refresh = '5'
        else:
            config = ConfigParser.ConfigParser()
            config.readfp(open(self.configfile))
            try:
                self.status_url = config.get('aptop', 'status_url')
                self.refresh = config.get('aptop', 'refresh')
            except:
                if os.path.isdir('/var/cpanel'):
                    self.status_url = 'http://localhost/whm-server-status'
                else:
                    self.status_url = 'http://localhost/server-status'
                self.refresh = '5'
        try:
            self.tree = lxml.html.parse(self.status_url)
        except:
            print "Apache not running or wrong mod_status url!?"
            sys.exit(1)

        # define should we filter out inactive sessions
        self.active = True
        self.sort_by = 'SS'
        # this is passed to reverse parameter on sort(list)
        self.sort_order = False

    def reverse_order(self):
        """ just reverese the ordering of current sorting """

        if self.sort_order:
            self.sort_order = False
        else:
            self.sort_order = True

    def refresh_rate(self):
        """
        (NoneType) -> int
        
        Returns parsed refresh time interval as int
        """
        return int(self.refresh)

    def fetch_status(self):
        """
        (NoneType) -> NoneType
        
        Refetching of data
        """
        if self.tree:
            old_tree = self.tree
        try:

            self.tree = lxml.html.parse(self.status_url)
        except:
            self.tree = old_tree

    def verify_mod_status(self):
        """
        (str) -> boolean
        
        Checks the data string for Apache Status title and returns true or
        false
        """
        return self.tree.find('.//title').text == 'Apache Status'

    def count_by_vhost(self, data):
        """
        (str) -> list of tuple
        
        Counts the active concurent connections by vhosts and returns an ordered
        list of tuples containing vhost name and number of active connections
        """
        vstatus = {}
        if self.active:
            vhosts = self.filter_active(data)
        else:
            vhosts = data
        for status in vhosts:
            if status['VHost'] in vstatus:
                vstatus[status['VHost']] += 1
            else:
                vstatus[status['VHost']] = 1
        items = vstatus.items()
        items.sort(key=itemgetter(1), reverse=True)

        return items

    def count_by_client(self, data):
        """
        (str) -> list of tuple
        
        Counts the active concurent connections by clients and returns an ordered
        list of tuples containing client IP and number of active connections
        """
        cstatus = {}
        if self.active:
            vhosts = self.filter_active(data)
        else:
            vhosts = data
        for status in vhosts:
            if status['Client'] in cstatus:
                cstatus[status['Client']] += 1
            else:
                cstatus[status['Client']] = 1
        items = cstatus.items()
        items.sort(key=itemgetter(1), reverse=True)

        return items

    def togle_active(self):
        if self.active:
            self.active = False
        else:
            self.active = True


    def filter_active(self, data):
        """
        (list of dict) -> list of dict
        
        Returns list of dicts based on filter status
        
        """
        filtered = []

        for status in data:
            if status['M'] != '_' and status['M'] != '.':
                filtered.append(status)
        return filtered


    def display_vhosts(self, data):
        """
        (list of dict) -> list of dict
        retrurn vhost data as list of dicts based on current filter 
        """
        if self.active:
            results = self.filter_active(data)
        else:
            results = data
        return results


    def parse_vhosts(self):
        """
        (str) -> list of dict
        
        Parses a apache status from internal class self.tree variable
        and returns list ofdict containing all vhost informations from 
        mod_status
        
        """
        tree = self.tree.xpath('//table[@border="0"]')[0]
        vhost_status = []
        headers = tree.findall('.//th')
        h2 = [s.text_content().replace('\n', '') for s in headers]
        for row in tree.findall('.//tr')[1:]: # this is header, excluding
            d = [s.text_content().replace('\n', '') for s in row.findall('.//td')]
            vhost_status.append(dict(zip(h2, d)))

        return sorted(vhost_status,
                      key=lambda k: float(k[self.sort_by]),
                      reverse=self.sort_order)

    def parse_header(self):
        """
        (NoneType) -> list
        
        Returns a list of header status variables from apache status page
        """

        headers = [h.text.replace('\n', '') for h in self.tree.findall('.//dt')]
        return headers
