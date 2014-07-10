__author__ = "branko@toic.org (http://toic.org)"
__date__ = "Dec 24, 2012 0:10 PM$"
__version__ = "0.3.2b"

import curses
from _curses import error as CursesError
import sys
import os
HEADER_HEIGHT = 5
FOOTER_HEIGHT = 2


class AptopCurses(object):

    def __init__(self, aptop):

        self.stdscr = curses.initscr()
        curses.noecho()
        curses.raw()
        curses.nonl()
        # Some terminals don't support different cursor visibilities
        try:
            curses.curs_set(0)
        except CursesError:
            pass

        # Some terminals don't support the default color palette
        try:
            curses.start_color()
            curses.use_default_colors()
        except CursesError:
            pass
        self.aptop = aptop
        self.MAX_H, self.MAX_W = self.stdscr.getmaxyx()
        self.running = True
        self.draw_view_keys = {
            'V': self.draw_vhosts,
            'H': self.draw_dashboard,
            'C': self.draw_clients,
            'U': self.draw_vhosts_with_uris
        }

        self.handle_view_keys = {
            'I': self.aptop.togle_active,
            'R': self.aptop.reverse_order,
            'Q': self.aptop_stop,
            'D': self.draw_update_refresh,
            'O': self.draw_update_order,
            'M': self.draw_update_http_methods
        }

        self.stdscr.nodelay(1)
        self.refresh = self.aptop.refresh_rate()
        self.counter = 0
        self.BODY_H = self.MAX_H
        self.view = 'H'
        curses.wrapper(self.start)

    def start(self, stdscr):
        if self.aptop.verify_mod_status():
            while self.running:
                self.aptop.fetch_status()
                self.BODY_H = self.MAX_H - HEADER_HEIGHT - FOOTER_HEIGHT
                c = self.stdscr.getch()
                if c in range(255):
                    key = str.upper(chr(c))
                    if key in self.draw_view_keys:
                        self.view = key
                    elif key in self.handle_view_keys:
                        self.handle_view_keys[key]()
                    self.counter = 0
                self.iterate()
        else:
            print "Apache not running or wrong mod_status url!"
            sys.exit(1)

    def draw_view(self):
        self.draw_header()
        # already filtered in the main loop
        self.draw_view_keys[self.view]()
        self.draw_footer()

    def iterate(self):
        if self.counter == 0:
            self.draw_view()
            self.counter = self.refresh * 2
        else:
            self.counter -= 1

        curses.napms(500)
        self.MAX_H, self.MAX_W = self.stdscr.getmaxyx()

    def aptop_stop(self):
        """ calling this will halt aptop"""
        if self.running:
            self.running = False

    """ Drawing output """

    def draw_update_refresh(self):
        ref = curses.newwin(self.MAX_H, self.MAX_W, 0, 0)

        running = True

        ref.addstr(10, 10, str('New refresh time in sec?'))
        # input handling
        acumulate = ''
        counter = 0
        while running:

            counter += 1
            c = self.stdscr.getch()
            if c in [curses.KEY_ENTER, curses.KEY_BREAK, 13]:
                try:
                    refresh = int(acumulate)
                    self.refresh = refresh
                    running = False
                except:
                    ref.addstr(12, 40, str('Not a valid input'))
                    ref.addstr(10, 35, str(' ') * (len(acumulate) + 20))
                    ref.addstr(10, 34, str(' '))
                    acumulate = ''
            else:
                if c in range(255):
                    if len(acumulate) < 1:
                        ref.addstr(12, 40, str('                  '))
                    try:
                        acumulate += chr(c)
                        ref.addstr(10, 35, str(acumulate))
                    except:
                        pass
            ref.refresh()
        # close input and exit the loop

    # TODO: build this somehow
    def draw_update_http_methods(self):
        methods_view = curses.newwin(self.MAX_H, self.MAX_W, 0, 0)

        running = True
        current = self.aptop.http_methods_active
        available = self.aptop.http_methods_available

        methods_view.addstr(1, 10, 'All available HTTP methods (default):')
        methods_view.addstr(2, 10, ','.join(available), curses.A_BOLD)

        methods_view.addstr(4, 10, 'Currently displayed HTTP methods:')
        methods_view.addstr(5, 10, ','.join(current), curses.A_BOLD)

        methods_view.addstr(7, 10, str('New methods filter:'))
        methods_view.addstr(8, 10, str('(type in the ones you\'re interested in, separating multiples with a comma. empty value defaults to all)'))
        fields = ''

        cancel_keys = [
            curses.KEY_ENTER,
            curses.KEY_BREAK,
            curses.KEY_HOME,
            # \r
            13,
            # esc
            27
        ]

        while running:
            c = self.stdscr.getch()
            if c in cancel_keys:
                if self.aptop.update_active_http_methods(fields):
                    running = False
                    break
                else:
                    methods_view.addstr(9, 50, str('Invalid input'))
                    methods_view.addstr(9, 45, str(' ') * (len(fields) + 20))
                    methods_view.addstr(9, 44, str(' '))
                    fields = ''
            else:
                try:
                    # TODO: handle backspace/delete properly?
                    fields += chr(c)
                    methods_view.addstr(9, 10, str(fields), curses.A_BOLD)
                except:
                    pass
            methods_view.refresh()
        # close input and exit the loop

    def draw_update_order(self):
        order = curses.newwin(self.MAX_H, self.MAX_W, 0, 0)

        running = True
        current = self.aptop.sort_options()
        order.addstr(1, 10, 'Available options are')
        opcount = 2
        for option in current[1]:
            if current[0] == option:
                order.addstr(opcount, 5, '*')
                order.addstr(opcount, 10, str(option))
            else:
                order.addstr(opcount, 10, str(option))
            opcount += 1

        order.addstr(10, 10, str('Type new ordering field?'))
        # input handling
        acumulate = ''
        while running:
            c = self.stdscr.getch()
            if c in [curses.KEY_ENTER, curses.KEY_BREAK, 13]:
                if self.aptop.update_sort_field(acumulate):
                    running = False
                else:
                    order.addstr(12, 40, str('Not a valid input'))
                    order.addstr(10, 35, str(' ') * (len(acumulate) + 20))
                    order.addstr(10, 34, str(' '))
                    acumulate = ''
            else:
                if c in range(255):
                    if len(acumulate) < 1:
                        order.addstr(12, 40, str('                  '))
                    try:
                        acumulate += chr(c)
                        order.addstr(10, 35, str(acumulate))
                    except:
                        pass
            order.refresh()
        # close input and exit the loop

    def draw_header(self):
        """ draws a header window """

        header = curses.newwin(HEADER_HEIGHT, self.MAX_W, 0, 0)
        header_data = self.aptop.parse_header()

        header1 = "%-5s: %s" % (
            'CPU Usage',
            header_data['CPU Usage']
        )

        header2 = "%-5s: %s %1s: %s" % (
            'Total Traffic',
            header_data['Total Traffic'],
            'Total accesses',
            header_data['Total accesses'],
        )

        header3 = "%-5s: %s %1s: %s" % (
            'busy childs',
            header_data['working childs'],
            'idle childs',
            header_data['idle childs'],
        )

        header4 = header_data['requests']

        header5 = "%-5s: %s" % (
            'Server uptime',
            header_data['Server uptime'],
        )

        header.addstr(0, 1, str(header1))
        header.addstr(1, 1, str(header2))
        header.addstr(2, 1, str(header3))
        header.addstr(3, 1, str(header4))
        header.addstr(4, 1, str(header5))
        header.refresh()

    def draw_dashboard(self):
        """ draws a dashboard window """
        dash = curses.newwin(self.BODY_H, self.MAX_W, HEADER_HEIGHT, 0)
        dash_data = self.aptop.display_vhosts(self.aptop.parse_vhosts())
        dcount = 0
        try:
            formatstr = '%-5s %1s %7s %3s %6s %7s %12s %-15s %-25s %-50s' % (
                'PID', 'M', 'CPU', 'SS', 'Req', 'Conn', 'Acc', 'Client',
                'VHost', 'Request')
            # fill up the remainder of screen estate with spaces properly
            formatstr = formatstr + (' ' * (self.MAX_W - len(formatstr)))
            dash.addstr(0, 0, formatstr, curses.A_REVERSE)
        except curses.error:
            pass
        for dash_line in dash_data:
            dcount += 1
            # dirty cpu missing fix for bug #5
            if 'CPU' in dash_line:
                cpu_value = dash_line['CPU']
            else:
                cpu_value = 'NaN'
            # end
            try:
                formatstr = '%-5s %1s %7s %3s %6s %7s %12s %-15s %-25s %s' % \
                    (
                        dash_line['PID'],
                        dash_line['M'],
                        cpu_value,
                        dash_line['SS'],
                        dash_line['Req'],
                        dash_line['Conn'],
                        dash_line['Acc'],
                        dash_line['Client'],
                        dash_line['VHost'][:26],
                        dash_line['Request']
                    )
                dash.addstr(dcount, 0, formatstr)
            except curses.error:
                pass
        dash.refresh()

    def draw_vhosts(self):
        """ draws a vhosts window """
        body = curses.newwin(self.BODY_H, self.MAX_W, HEADER_HEIGHT, 0)

        body_data = self.aptop.count_by_vhost(self.aptop.parse_vhosts())
        bcount = 0
        try:
            body.addstr(0, 0, str(" ") * self.MAX_W, curses.A_REVERSE)
            body.addstr(bcount, 1, 'Num req', curses.A_REVERSE)
            body.addstr(bcount, 20, "Virtualhost", curses.A_REVERSE)
        except curses.error:
            pass
        for body_line in body_data:
            bcount += 1
            try:
                body.addstr(bcount, 1, str(body_line[1]))
                body.addstr(bcount, 20, str(body_line[0]))
            except curses.error:
                pass
        body.refresh()

    def draw_clients(self):
        """ draws a vhosts window """
        body = curses.newwin(self.BODY_H, self.MAX_W, HEADER_HEIGHT, 0)
        body_data = self.aptop.count_by_client(self.aptop.parse_vhosts())
        bcount = 0
        try:
            body.addstr(0, 0, str(" ") * self.MAX_W, curses.A_REVERSE)
            body.addstr(bcount, 1, 'Num req', curses.A_REVERSE)
            body.addstr(bcount, 20, "Client IP", curses.A_REVERSE)
        except curses.error:
            pass
        for body_line in body_data:
            bcount += 1
            try:
                body.addstr(bcount, 1, str(body_line[1]))
                body.addstr(bcount, 20, str(body_line[0]))
            except curses.error:
                pass
        body.refresh()

    def draw_vhosts_with_uris(self):
        """ draws the 'requests-grouped-by-vhosts' window """
        body = curses.newwin(self.BODY_H, self.MAX_W, HEADER_HEIGHT, 0)

        body_data = self.aptop.count_and_group_requests_by_vhost(
            self.aptop.parse_vhosts()
        )
        linecount = 0

        try:
            body.addstr(0, 0, str(" ") * self.MAX_W, curses.A_REVERSE)
            body.addstr(linecount, 1, 'Num req', curses.A_REVERSE)
            body.addstr(linecount, 20, 'URI', curses.A_REVERSE)
        except curses.error:
            pass

        for vhost, vhost_data in body_data:
            linecount += 1
            requests = vhost_data['reqs']
            vhost_str = str(
                '>>> ' + vhost + ' (' + str(vhost_data['cnt']) + ')'
            )

            try:
                body.addstr(linecount, 1, vhost_str, curses.A_BOLD)
                linecount += 1
                for k, v in requests:
                    body.addstr(linecount, 1, str(v))
                    body.addstr(linecount, 20, str(k))
                    linecount += 1
            except curses.error:
                pass

        body.refresh()

    def draw_footer(self):
        """ draws a footer window """
        footer = curses.newwin(
            FOOTER_HEIGHT,
            self.MAX_W,
            self.MAX_H - FOOTER_HEIGHT,
            0
        )
        try:
            footer.addstr(1, 1, 'Q')
            footer.addstr(1, 3, 'Quit ApTOP', curses.A_REVERSE)
            footer.addstr(1, 14, 'H')
            footer.addstr(1, 16, 'Home', curses.A_REVERSE)
            footer.addstr(1, 26, 'V')
            footer.addstr(1, 28, 'By Vhost', curses.A_REVERSE)
            footer.addstr(1, 37, 'C')
            footer.addstr(1, 39, 'By Client', curses.A_REVERSE)
            footer.addstr(1, 50, 'U')
            footer.addstr(1, 52, 'By Vhost/URIs', curses.A_REVERSE)
        except curses.error:
            pass
        footer.refresh()
