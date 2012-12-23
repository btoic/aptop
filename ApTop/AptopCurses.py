__author__ = "branko@toic.org (http://toic.org)"
__date__ = "Dec 24, 2012 0:10 PM$"
__version__ = "0.2.3b"

import curses
import sys

HEADER_HEIGHT = 10
FOOTER_HEIGHT = 2

class AptopCurses(object):
	def __init__(self, aptop):

		self.stdscr = curses.initscr()
		self.aptop = aptop
		self.MAX_H, self.MAX_W = self.stdscr.getmaxyx()
		self.running = True
		self.draw_view_keys = {
			'V': self.draw_vhosts,
		  	'H': self.draw_dashboard,
		  	'C': self.draw_clients,
		  						}

		self.handle_view_keys = {
			'I': self.aptop.togle_active,
			'R': self.aptop.reverse_order,
		  	'Q': self.aptop_stop,
		  	'D': self.draw_update_refresh,
		  	'O': self.draw_update_order,
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
		while running:
			c = self.stdscr.getch()
			if c in [curses.KEY_ENTER, curses.KEY_BREAK, 10]:
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
			if c in [curses.KEY_ENTER, curses.KEY_BREAK, 10]:
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

