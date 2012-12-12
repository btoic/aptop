ApTop
=====

ApTop ia a top(1) alike monitoring utility for Apache.

Being daily involved in monitoring system load in shared environment I find it lacking proper tool for monitoring Apache behavior in real time. Granted there are some tools for this job, they are usually of limited options for some monitoring needs.

ApTop was written as a hobby project in python for debugging purposes while investigating several system load situations caused by web applications in shared hosting environment.

ApTop is still an early beta release with some known bugs, nevertheless it still provides a great starting point in monitoring Apache. Every feedback and feature request at this point is more than welcomed.


Description
-----------

ApTop will show near real time Apache active working proceses and virtual host connections. By default sleeping / waiting for connections slots will be filtered out. 

ApTop is also displaying several screens 

************************
Dashboard or Home screen
************************

This screen displays some relevant informations gathered from `apache-status <http://httpd.apache.org/docs/2.2/mod/mod_status.html>`_ page.
It is by default sorted by shortest last apache access time "SS" and it displays only active connections. Displayed fields are the same as in server-status page, so you can find detailed explanation for their meaning at the bottom of server-status page.

Displayed fields are:

PID - OS process ID
M - Mode of operation
CPU - CPU usage, number of seconds
SS - Seconds since beginning of most recent request<
Req - Milliseconds required to process most recent request
Conn - Kilobytes transferred this connection
Acc - Number of accesses this connection / this child / this slot
Client - Remote client
VHost - Local virtualhost
Request - Request method and partial URL

**********************
Count by vhosts screen
**********************

This screen displays virtualhosts in order by highest count of active connections along with connection count.

Very useful for detecting high traffic sites.

***********************
Count by clients screen
***********************

This screen displays clients in order by highest count of active connections along with connection count.

Very useful for detecting resource exhausters.


Requirements
------------
ApTop should work just fine on any unix based system with python standard
packages and lxml.

Make sure you have libxml2 libxslt libxslt-devel libxml2-devel packages instaleld
prior to building lxml:

For RHEL based distro you can install those with

::

  yum install libxml2 libxslt libxslt-devel libxml2-devel

After that you can install lxml python package with **easy_install lxml** or **pip install lxml**

ApTop is using Apaches **mod_status** with **ExtendedStatus On** for gathering data.
Please ensure that **mod_status** is enabled and proper status url is defined in **aptop.conf**
There are some concernes regarding enabled ExtendedStatus On, but I think `this links <http://www.philchen.com/2008/06/02/apache-20-mod_status-effects-on-performance-server-resources>`_ covers this nicely.

Instalation
-----------

These installation options are for RHEL based distros, adjust accordingly.
yum install libxml2 libxslt libxslt-devel libxml2-devel python-setuptools
easy_install https://bitbucket.org/btoic/aptop/get/master.tar.gz


Configuration
-------------

ApTop has some built in default configuration directives, but it will also look first in ~/.aptop.conf and than /etc/aptop.conf for overrides.

ApTop uses .ini style configuration files and main cofniguration options should be
placed after **[aptop]** section.

By default ApTop will use http://localhost/server-status url for grabbing 
data to display, and with default refresh rate of 5 seconds.

********************************
Available configuration options:
********************************

 status_url = URL

This configuration option will require you to enter valid mod_status status url
for server you wish to monitor.
This defaults to http://localhost/server-status
Note that Apache should have ExtendedStatus conf option set to On

 refresh = seconds

This option will control ApTop default refresh interval. It defaults 
to 5 seconds and can't be lower than 1 second.

You can even monitor the remote systems if they granted you access rights to theirs server-status URL.
In the future ApTop will provide options to save remote monitored servers to its configuration.

Runtime options
---------------

While running ApTop responds to following options:

**H** - display main screen

**V** - display vhosts by conn. count

**c** - display clients by conn. count

**R** - reverse the current sort order

**I** - toggle active/inactive slots


Aditional links
---------------

http://toic.org

https://bitbucket.org/btoic/aptop