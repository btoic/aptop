__author__ = "branko@toic.org (http://toic.org)"
__date__ = "Dec 9, 2012 2:00 PM$"
__version__ = "0.2.0a"

import curses
import time
import sys

HEADER_HEIGHT = 10
FOOTER_HEIGHT = 2


class AptopCurses(object):
	def __init__(self, aptop):
		self.stdscr = curses.initscr()
		self.aptop = aptop
		self.MAX_H, self.MAX_W = self.stdscr.getmaxyx()

		self.stdscr.nodelay(1)
		self.refresh = self.aptop.refresh_rate()
		self.counter = 0
		self.BODY_H = self.MAX_H
		self.view = 'V'
		curses.wrapper(self.start)


	def start(self, stdscr):
		curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
		curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
		if self.aptop.verify_mod_status():
			while 1:
				self.aptop.fetch_status()
				self.BODY_H = self.MAX_H - HEADER_HEIGHT - FOOTER_HEIGHT
				c = self.stdscr.getch()
				if c == ord('q') or c == ord('Q'): break
				elif c == ord('v') or c == ord('V'):
					self.view = 'V'
				elif c == ord('d') or c == ord('D'):
					self.view = 'D'

				self.draw_view()
		else:
			print "Apache not running or wrong mod_status url!"
			sys.exit(1)

	def draw_view(self):
		self.draw_header()

		if self.view == 'V':
			self.draw_vhosts()
		elif self.view == 'D':
			self.draw_dashboard()
		else:
			print "something went wrong"
			sys.exit(1)
		self.draw_footer()
		self.iterate()

	def iterate(self):
		time.sleep(self.refresh)
		self.MAX_H, self.MAX_W = self.stdscr.getmaxyx()



	def draw_header(self):
		""" draws a header window """
		header = curses.newwin(
								HEADER_HEIGHT,
								self.MAX_W,
								0, 0
								)
		header_data = self.aptop.parse_header()
		hcount = 0
		for header_line in header_data:
			header.addstr(hcount, 1, str(header_line[:self.MAX_W - 2]))
			hcount += 1
		header.refresh()

	def draw_dashboard(self):
		""" draws a dashboard window """
		dash = curses.newwin(
							self.BODY_H,
							self.MAX_W,
							HEADER_HEIGHT, 0
							)

		dash_data = self.aptop.display_vhosts(self.aptop.parse_vhosts())
		dcount = 1
		dash.addstr(0, 0, str(" ") * self.MAX_W, curses.A_REVERSE)
		dash.addstr(dcount, 1, str('Virtualhost'), curses.A_BOLD)
		dash.addstr(dcount, 25, str('Client'), curses.A_BOLD)
		for dash_line in dash_data:
			dcount += 1
			if dcount < self.BODY_H:
				dash.addstr(dcount, 1, str(dash_line['VHost']))
				dash.addstr(dcount, 25, str(dash_line['Client']))
		dash.refresh()

	def draw_vhosts(self):
		""" draws a vhosts window """
		body = curses.newwin(
							self.BODY_H,
							self.MAX_W,
							HEADER_HEIGHT, 0
							)

		body_data = self.aptop.count_by_vhost(self.aptop.parse_vhosts())
		bcount = 1
		body.addstr(0, 0, str(" ") * self.MAX_W, curses.A_REVERSE)
		body.addstr(1, 1, 'Num req', curses.A_BOLD)
		body.addstr(1, 20, "Virtualhost", curses.A_BOLD)
		for body_line in body_data:
			bcount += 1
			if bcount < self.BODY_H:
				body.addstr(bcount, 1, str(body_line[1]))
				body.addstr(bcount, 20, str(body_line[0]))
		body.refresh()

	def draw_footer(self):
		""" draws a footer window """
		footer = curses.newwin(
								FOOTER_HEIGHT,
								self.MAX_W,
								self.MAX_H - FOOTER_HEIGHT, 0
								)
		footer.addstr(1, 1, 'Q')
		footer.addstr(1, 3, ' Quit ApTOP', curses.A_REVERSE)
		footer.addstr(1, 15, 'D')
		footer.addstr(1, 17, ' Dashbord', curses.A_REVERSE)
		footer.addstr(1, 27, 'V')
		footer.addstr(1, 29, ' By Vhost', curses.A_REVERSE)
		footer.refresh()

