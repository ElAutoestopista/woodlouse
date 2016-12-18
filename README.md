# woodlouse
## Woodlouse - No-IP script for provider Gandi.net

Sergio Fernandez Cordero <sergio@fernandezcordero.net>
twitter: http: //twitter.com/elautoestopista
http://www.fernandezcordero.net/blog

##### Requires Python3.X. For Python2.X, use v1.x instead

1. CHANGELOG
2. LICENSE AND DISCLAIMER
3. USAGE
4. Parallel executions
5. AUTHOR'S NOTE

1.CHANGELOG
------------

* Refactor for Python3.X
* Better logging management
* Exception management
* Take config parameters from config file instead of arguments.
* Cleaner, funnier.


2.- LICENSE AND DISCLAIMER
---------------------------

License GPLv3 - https://www.gnu.org/copyleft/gpl.html - see LICENSE for details

3.- USAGE
--------

Usage: python woodlouse

Now all requiered config mut bge put on file config.py. In a future release, you could set woodlouse to use different
config file. Fields are below:

**ZONE**: DNS name assigned to the domain Zone. When the record is created, it will be created for all domains
using that area.

**TTL**: The lifetime should be a very low value, so that other DNS servers have little time entry
cached, so they have to frequently check and take the changes that occur. For instance
5 minutes or less.

**REGISTRY**: Registry value you want to create, without the domain name (as an area can be used in multiple domains).
For example: To create "www.midominio.com" record would be "www". At this time, only A registry types are supported.

**APIKEY**: API key provided by Gandi.net to enable the use of the API.

**ENV**: The modifier prod launches operations into the production environment, the changes are real.
The switch test launch operations against the OT & E environment, there exist only operations.
NOTE: Be sure to create a consistent environment in OT & E before you begin tinkering (check the
API documentation Gandi (http://doc.rpc.gandi.net/)

**LOGS**: Absolute path of Directory where log files will bem ended with backslash (/). Ensure you have permissions to
write on it.

4. Parallel executions
---------------------

No parallel execution is supported at this time.

5. AUTHOR'S NOTE
-------------------

This program is a work in progress. Just for fun. Pull Requests welcome.

This work is dedicated to my baby Noelia, my beloved "woodlouse" :)
