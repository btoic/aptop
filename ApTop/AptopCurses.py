__author__ = "branko@toic.org (http://toic.org)"
__date__ = "Dec 9, 2012 2:00 PM$"
__version__ = "0.2.1b"

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
		self.view = 'H'
		curses.wrapper(self.start)


	def start(self, stdscr):
		if self.aptop.verify_mod_status():
			while 1:
				self.aptop.fetch_status()
				self.BODY_H = self.MAX_H - HEADER_HEIGHT - FOOTER_HEIGHT
				c = self.stdscr.getch()
				if c == ord('q') or c == ord('Q'): break
				elif c == ord('v') or c == ord('V'):
					self.view = 'V'
				elif c == ord('h') or c == ord('H'):
					self.view = 'H'
				elif c == ord('c') or c == ord('C'):
					self.view = 'C'
				elif c == ord('i') or c == ord('I'):
					self.aptop.togle_active()
				elif c == ord('r') or c == ord('R'):
					self.aptop.reverse_order()
				self.draw_view()
		else:
			print "Apache not running or wrong mod_status url!"
			sys.exit(1)

	def draw_view(self):
		self.draw_header()

		if self.view == 'V':
			self.draw_vhosts()
		elif self.view == 'H':
			self.draw_dashboard()
		elif self.view == 'C':
			self.draw_clients()
		else:
			print "something went wrong"
			sys.exit(1)
		self.draw_footer()
		self.iterate()

	def iterate(self):
		curses.napms(self.refresh * 1000)
		#time.sleep(self.refresh)
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
			try:
				header.addstr(hcount, 1, str(header_line[:self.MAX_W - 2]))
			except curses.error:
				pass
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
		dcount = 0
		try:
			formatstr = '%-5s %1s %7s %3s %6s %7s %12s %-15s %-25s %-50s' % (
				'PID', 'M', 'CPU', 'SS', 'Req', 'Conn', 'Acc', 'Client', 'VHost',
				'Request' + ' ' * self.MAX_W)

			dash.addstr(0, 0, formatstr, curses.A_REVERSE)
		except curses.error:
			pass
		for dash_line in dash_data:
			dcount += 1
			try:
				formatstr = '%-5s %1s %7s %3s %6s %7s %12s %-15s %-25s %s' % (
				dash_line['PID'], dash_line['M'], dash_line['CPU'],
				dash_line['SS'], dash_line['Req'], dash_line['Conn'],
				dash_line['Acc'], dash_line['Client'], dash_line['VHost'][:26],
				dash_line['Request'])
				dash.addstr(dcount, 0, formatstr)
			except curses.error:
				pass
		dash.refresh()

	def draw_vhosts(self):
		""" draws a vhosts window """
		body = curses.newwin(
							self.BODY_H,
							self.MAX_W,
							HEADER_HEIGHT, 0
							)

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
		body = curses.newwin(
							self.BODY_H,
							self.MAX_W,
							HEADER_HEIGHT, 0
							)

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

	def draw_footer(self):
		""" draws a footer window """
		footer = curses.newwin(
								FOOTER_HEIGHT,
								self.MAX_W,
								self.MAX_H - FOOTER_HEIGHT, 0
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
		except curses.error:
			pass
		footer.refresh()

