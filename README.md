## Woodlouse - No-IP script for provider Gandi.net

Woodlouse is a simple python script which can dinamically change
your DNS registry in a Gandi.net domain when your public IP
changes, just like a no-ip but your own!

Just get an API key, the information about your domain, and put
a cron job to enjoy!

Executed every 10 minutes, woodlouse will check your public IP 
using five different services. Then, will check against Gandi.net
which IP is actually configured in the DNS registry you specified.
If the IP is different, woodlouse automatically will change the
DNS registry via the Gandi.net Domain API XML-RPC. Several time
later (from seconds to 48h, due to DNS propagation), the registry
will point to the new IP from every Internet.

Woodlouse is ideal for home users who want an Internet service
hosted at home, but don't want or can't afford a static public IP.
It has been working for me at home since years!

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
cached, so they have to frequently check and take the changes that occur. Note that Gandi.net has a minimum of 300 secs.

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
