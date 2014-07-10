__author__ = "branko@toic.org (http://toic.org)"
__date__ = "Dec 24, 2012 0:10 PM$"
__version__ = "0.3.2b"

import ConfigParser
import os
import sys
from operator import itemgetter

try:
    import lxml.html  # @UnresolvedImport
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
        self.configfile = None

        homedir = os.path.expanduser('~')
        homeconf = os.path.join(homedir, '.aptop.conf')

        test_conf_files = [homeconf, '/etc/aptop.conf']
        for f in test_conf_files:
            if os.path.isfile(f):
                self.configfile = f
                break

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
            except:
                if os.path.isdir('/var/cpanel'):
                    self.status_url = 'http://localhost/whm-server-status'
                else:
                    self.status_url = 'http://localhost/server-status'
            try:
                self.refresh = config.get('aptop', 'refresh')
            except:
                self.refresh = '5'
        try:
            self.tree = lxml.html.parse(self.status_url)
        except:
            print "Apache not running or wrong mod_status url!?"
            sys.exit(1)

        # define should we filter out inactive sessions
        self.active = True
        self.sort_by = 'SS'
        # key case must be defined exactly as named in data source
        self.sort_fields = {
            'SS': 'float',
            'CPU': 'float',
            'Req': 'float',
            'Conn': 'float',
            'VHost': 'str',
            'Request': 'str'
        }
        # filterable http methods
        self.http_methods_available = [
            'GET', 'HEAD', 'POST', 'PUT', 'DELETE',
            'TRACE', 'OPTIONS', 'CONNECT', 'PATCH'
        ]
        # show all methods by default
        self.http_methods_active = self.http_methods_available
        # self.http_methods_active = ['OPTIONS', 'POST']
        # this is passed to reverse parameter on sort(list)
        self.sort_order = False

    def http_method_options(self):
        """ (NoneType) -> list of string and dict

            Returns the current self.http_methods_active and self.http_methods_available
        """
        return [self.http_methods_active, self.http_methods_available]

    def sort_options(self):
        """ (NoneType) -> list of string and dict

           Returns the current self.sort_fields and self.sort_by variable
        """
        return [self.sort_by, self.sort_fields]

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

        Counts the active concurent connections by vhosts and returns an
        ordered list of tuples containing vhost name and number of active
        connections
        """
        vstatus = {}
        if self.active:
            vhosts = self.filter_active(data)
        else:
            vhosts = data
        vhosts = self.filter_http_methods(data)
        for status in vhosts:
            if status['VHost'] in vstatus:
                vstatus[status['VHost']] += 1
            else:
                vstatus[status['VHost']] = 1
        items = vstatus.items()
        items.sort(key=itemgetter(1), reverse=self.sort_order)

        return items

    def count_by_client(self, data):
        """
        (str) -> list of tuple

        Counts the active concurent connections by clients and returns an
        ordered list of tuples containing client IP and number of active
        connections
        """
        cstatus = {}
        if self.active:
            vhosts = self.filter_active(data)
        else:
            vhosts = data
        vhosts = self.filter_http_methods(data)
        for status in vhosts:
            if status['Client'] in cstatus:
                cstatus[status['Client']] += 1
            else:
                cstatus[status['Client']] = 1
        items = cstatus.items()
        items.sort(key=itemgetter(1), reverse=self.sort_order)

        return items

    def count_and_group_requests_by_vhost(self, data):
        """
        (str) -> list of tuples

        Groups, counts and sorts the requests per vhost.
        Then sorts the resulting list by the total number
        of requests per vhost
        """
        grouped = {}
        if self.active:
            vhosts = self.filter_active(data)
        else:
            vhosts = data

        vhosts = self.filter_http_methods(vhosts)

        for status in vhosts:

            vhost = status['VHost']
            req_uri = status['Request']

            if vhost in grouped:
                if req_uri in grouped[vhost]:
                    grouped[vhost][req_uri] += 1
                else:
                    grouped[vhost][req_uri] = 1
            else:
                grouped[vhost] = {}
                grouped[vhost][req_uri] = 1

        # TODO: not loving this, but it seems to work for now
        for vhost in grouped:
            vhost_requests = sorted(
                grouped[vhost].items(),
                key=lambda x: (x[1], x[0]),
                reverse=self.sort_order
            )
            count = sum(x[1] for x in vhost_requests)
            grouped[vhost] = {'reqs': vhost_requests, 'cnt': count}

        grouped_sorted = sorted(
            grouped.items(),
            key=lambda x: (x[1].values()[0], x[0]),
            reverse=self.sort_order
        )
        return grouped_sorted

    def count_by_request(self, data):
        """
        (str) -> list of tuples

        Counts the active requests and returns an ordered
        list of tuples containing the request URI and the matching number
        of active connections
        """
        rstatus = {}
        if self.active:
            vhosts = self.filter_active(data)
        else:
            vhosts = data
        vhosts = self.filter_http_methods(data)
        for status in vhosts:
            if status['Request'] in rstatus:
                rstatus[status['Request']] += 1
            else:
                rstatus[status['Request']] = 1
        items = rstatus.items()
        items.sort(key=itemgetter(1), reverse=self.sort_order)

        return items

    def togle_active(self):
        if self.active:
            self.active = False
        else:
            self.active = True

    def update_sort_field(self, field):
        for key in self.sort_fields:
            if field.lower() == key.lower():
                self.sort_by = key
                return True
        return False

    def update_active_http_methods(self, fields):
        # convert a possible comma-separeted list of methods into a list
        if isinstance(fields, basestring):
            fields = map(str.strip, fields.split(','))
            fields = filter(None, fields)

        # default to all available methods for falsy values
        # (which should include empty strings/lists)
        if not fields:
            fields = self.http_methods_available

        self.http_methods_active = fields
        return True

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

    def filter_http_methods(self, data):
        """
        (list of dict) -> list of dict
        Returns the filtered list of dicts based on http methods we're currently interested in
        """
        filtered = []
        for status in data:
            if status['Method'] in self.http_methods_active:
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
        results = self.filter_http_methods(results)
        return results

    def sort_vhosts_by(self, values, sort_method):

        if sort_method == 'float':
            return sorted(
                values,
                key=lambda k: float(k[self.sort_by]),
                reverse=self.sort_order
            )
        elif sort_method == 'str':
            return sorted(
                values,
                key=lambda k: str(k[self.sort_by]),
                reverse=self.sort_order
            )

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
        h2.append("Method")
        for row in tree.findall('.//tr')[1:]:  # this is header, excluding
            d = [
                s.text_content().replace('\n', '')
                for s in row.findall('.//td')
            ]
            try:
                http_method = d[-1].split()[0]
            except IndexError:
                http_method = '?'
            d.append(http_method)
            vhost_status.append(dict(zip(h2, d)))

        return self.sort_vhosts_by(
            vhost_status,
            self.sort_fields[self.sort_by]
        )

    def parse_header(self):
        """
        (NoneType) -> list

        Returns a dictionary of header status variables from apache status
        page.

        Available header fields:
           -  Server Version
           -  Server Built
           -  Current Time
           -  Restart Time
           -  Server uptime
           -  Parent Server Generation
           -  CPU Usage
           -  Total accesses
           -  Total Traffic
           -  working childs #requests currently being processed by the server
           -  idle childs    #idle workers
           -  requests
        """

        HEADER_LIST = [
            'Server Version:',
            'Server Built:',
            'Current Time:',
            'Restart Time:',
            'Parent Server Generation:',
            'Server uptime:',
            'Total accesses:',
            'CPU Usage:',
            'requests/sec',
            'workers',
        ]

        headers = {}

        for h in self.tree.findall('.//dt'):
            line = h.text.replace('\n', '')
            for item in HEADER_LIST:
                if item in line:

                    if item == 'workers':
                        for req in line.split(','):
                            req = req.strip()
                            if req.split()[-1] == 'processed':
                                headers['working childs'] = req.split()[0]
                            elif req.split()[-1] == 'workers':
                                headers['idle childs'] = req.split()[0]
                    elif item == 'requests/sec':
                        headers['requests'] = line

                    elif item == 'Total accesses:':
                        for el in line.split('-'):
                            el = el.strip()
                            key = el.split(':')[0].strip()
                            value = el.split(':')[1].strip()
                            headers[key] = value

                    else:
                        headers[item[:-1]] = line.split(':')[1].strip()

        return headers
