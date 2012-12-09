#!/usr/bin/env python

from ApTop import ApacheStatus
import curses
import time
import sys

def aptop_main(stdscr):
    a = ApacheStatus()
    ref_rate = a.refresh_rate()
    #ostaje naknadno za definirati color sheme
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
    stdscr.nodelay(1)
    header_height = 10
    footer_height = 2
    if a.verify_mod_status():
        while 1:
            a.fetch_status()
            max_height, max_width = stdscr.getmaxyx()
            body_height = max_height - header_height - footer_height
            c = stdscr.getch()
            if c == ord('q') or c == ord('Q') : break
            else:

                header = curses.newwin(
                                       header_height,
                                       max_width,
                                       0, 0)

                body = curses.newwin(
                                     body_height,
                                     max_width,
                                     header_height, 0)

                footer = curses.newwin(
                                       footer_height,
                                       max_width,
                                       max_height - footer_height, 0
                                       )
                header_data = a.parse_header()
                hcount = 0
                for header_line in header_data:
                    header.addstr(hcount, 1, str(header_line[:max_width - 2]))
                    hcount += 1

                body_data = a.count_by_vhost(a.parse_vhosts())
                bcount = 1
                body.addstr(0, 0, str(" ") * max_width, curses.color_pair(1))
                body.addstr(1, 1, 'Num req', curses.A_BOLD)
                body.addstr(1, 20, "Virtualhost", curses.A_BOLD)
                for body_line in body_data:
                    bcount += 1
                    if bcount < body_height:
                        body.addstr(bcount, 1, str(body_line[1]))
                        body.addstr(bcount, 20, str(body_line[0]))

                footer.addstr(1, 1, 'Q', curses.color_pair(3))
                footer.addstr(1, 3, ' Quit ApTOP', curses.color_pair(2))

                header.refresh()
                body.refresh()
                footer.refresh()
                time.sleep(ref_rate)
    else:
        #maybe add some helpfull message
        sys.exit(1)

if __name__ == "__main__":

    stdscr = curses.initscr()
    curses.wrapper(aptop_main)
