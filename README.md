ApTop ia a top(1) alike monitoring utility for Apache.
Requirements
============

Requires additional python packages lxml.
You can install those with easy_install lxml or pip install lxml

It also requires mod_status active in apache and ExtendedStatus On

ApTop will look for /etc/aptop.conf or ~/.aptop.conf for configuration options
By default aptop will use http://localhost/server-status url for grabbing 
data for display. You can override this with status_url conf variable.

Configuration
=============

ApTop will use some default values if configuration files are not found
system wide configuration file will be automaticaly placed in /etc/aptop.conf
You can override this conf file by placing your own configuration inside
~/.aptop.conf file. Theroreticly this way you can also display ApTop for remote
servers granting you access rigts on /server-status url.

ApTop uses .ini style configuration files. Main cofniguration options should be
placed after [aptop] directive

Available configuration options:

status_url = URL

This configuration option will require you to enter valid mod_status status url
for server you wish to monitor.
This defaults to http://localhost/server-status
Note that Apache should have ExtendedStatus conf option set to On

refresh = seconds

This option will control ApTop default refresh interval. It defaults 
to 5 seconds and can't be lower than 1 second. 

