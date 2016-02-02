#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
 Woodlouse v1.1.4 NeXTGen

  No-IP type script for the provider Gandi.net

  Sergio Fernandez Cordero <sergio@fernandezcordero.net>
  twitter: http: //twitter.com/elautoestopista
  http://www.fernandezcordero.net/blog

  License GPLv3 - https://www.gnu.org/copyleft/gpl.html - see LICENSE for details

  CHANGELOG:
  ----------
      - List of IP services for public consultation. Supports failover
      - Already use pylint! :)
      - PEP8 compliant !!
      - Implemented using different log files depending on issue # 3
      - Locking system it is implemented to avoid the problem of corrupt DNS zone in concurrent executions.

  USAGE:
  ------
	python woodlouse.py zone TTL REGISTRY apikey (prod / test)
  TODO:
  -----
      - Error control: Currently, an error creating an entry
	nonexistent, creating the area although not activated. This produces
	amount of waste.
'''

import xmlrpclib
import sys
import datetime
import os
import requests
import time

# If no arguments, and use the program banner is received
# We define the messages that build exits

MENSA_BANNER = "Woodlouse v1.1.1 NeXTGen - Sergio Fernández Cordero 2014\n"
MENSA_LICEN = "Este programa se distribuye con licencia GPLv3 - https://www.gnu.org/copyleft/gpl.html .\n"
MENSA_USO = "\nUsage: python woodlouse.py zone ttl REGISTRY apikey (prod/test)"
ERROR_ARG = "Error: Woodlouse only accepts 3 arguments.\n"
ERROR_TTL = "Error: TTL must be an integer.\n"
ERROR_ENV = "Error: Environment must be prod o test"
ERROR_API = "Error: Invalid API key."
ERROR_REGISTRO_CADENA = "Error: REGISTRY must be a string.\n"
ERROR_ZONA_CADENA = "Error: ZONE must be a string.\n"
ERROR_ENTORNO = "Error: Environment must be prod (Production) or test (OT&E).\n"
ERROR_LOGDIR = "ERROR: Logs directory doesn't exists. Will be created."
ACTIVA_OK = "Activation successful. Returned "
ACTIVA_KO = "Activation error. Returned "
DELETE_OK = "Deletion succesful. Returned "
DELETE_KO = "Deletion error. Returned "

# Locate the current working path, where it is the script

RUTA = sys.path[0]

if len(sys.argv) == 1:
    print MENSA_BANNER + MENSA_LICEN + MENSA_USO
    sys.exit(1)

# If they received more than three or less than three arguments, and output Error
elif len(sys.argv) - 1 != 5:
    print ERROR_ARG + MENSA_USO
    sys.exit(1)

# Check that last argument as TTL is an integer
# Then we will turn to type int

# TTL. st your discrection

if sys.argv[2].isdigit():
    TIEMPO_VIDA = int(sys.argv[2])
else:
    print ERROR_TTL + MENSA_USO
    sys.exit(1)

# Assign the input arguments
# The area that you have assigned to your domain.
# If the area is used by multiple domains, registration
# Will be created in all of them.

ID_ZONA = sys.argv[1]


# Name of the record that we want to create
# (Do not put the domain name back, it's automatically added)

NOMBRE = sys.argv[3]

# API key
# Check that you have 24 characters without spaces

if len(sys.argv[4]) == 24 and not (' ' in sys.argv[4]):
    APIKEY = sys.argv[4]
else:
    print ERROR_API + MENSA_USO
    sys.exit(1)

# Environment: Production o Test (OT&E)
if (sys.argv[5] == "prod" or sys.argv[5] == "test"):
    ENTORNO = sys.argv[5]
else:
    print ERROR_ENV + MENSA_USO
    sys.exit(1)

# Check REGISTRY and ZONE are strings

if not isinstance(NOMBRE, str):
    print ERROR_REGISTRO_CADENA + MENSA_USO
    sys.exit(1)
if not isinstance(ID_ZONA, str):
    print ERROR_ZONA_CADENA + MENSA_USO
    sys.exit(1)

# Check environment is PROD or TEST
if ENTORNO == "prod":
    # Load the API Gandi.net
    # Production environment

    API = xmlrpclib.ServerProxy('https://rpc.gandi.net/xmlrpc/')
elif ENTORNO == "test":
    # Test environment(OT&E)

    API = xmlrpclib.ServerProxy('https://rpc.ote.gandi.net/xmlrpc/')
else:
    print ERROR_ZONA_CADENA + MENSA_USO
    sys.exit(1)

# Initial definitions

ZONA = API.domain.zone.list(APIKEY, {'name': ID_ZONA})
if not ZONA:
    print "Zone "+ID_ZONA+" doesn't exists"
    sys.exit(1)
else:
    ZONE_ID = ZONA[0]['id']
    ZONE_NOMBRE = ZONA[0]['name']

# We define the date and time of execution

MOMENTO = datetime.datetime.now()
FECHA = MOMENTO.strftime('%d %b %Y %H:%M - ')

# We define the log files
# Check that the directory exists logs

# We build the paths to the log files.

DIR_RUTA = RUTA+"/logs"
if not os.path.isdir(DIR_RUTA):
    print ERROR_LOGDIR
    os.mkdir(DIR_RUTA)

# The file where the last execution are stored always overwrites
DIR_OPERACIONES = RUTA+"/logs/operations.log"
NOACTUA = open(DIR_OPERACIONES, "w")

# The file where the changes are stored only be created if there
# If it exists, the new data will be added at the end

DIRCAMBIOS = RUTA+"/logs/changes.log"
ACTUA = open(DIRCAMBIOS, "a")  # "a" includes writing if the file does not exist

# Check the IP we have today
# The function provides access various services to determine the IP
# Published the team.


def ip_publica():
    """

       ip_publica() It uses various services to check IP issues
       of the team. If one is not available, use the following in
       the list.

       You can add additional services by adding elements to the array

    """

    for service in ['http://icanhazip.com/',
                    'http://curlmyip.com/',
                    'http://ident.me/',
                    'http://ipof.in/txt/',
                    'http://ifconfig.me/ip/']:
        try:
            IP = requests.get(service).text
            return service, IP
        except requests.exceptions.ConnectionError:
            pass

    # If no one is available, bad luck
    return None

# Call to check function IP
# And evaluation of results

IP_RESOURCE = ip_publica()

if IP_RESOURCE:
    RECURSO = IP_RESOURCE[0]
    ACTUALIP = IP_RESOURCE[1]
    MENSA_SERVICIO = "Using service"+RECURSO+" get IP "+ACTUALIP+"\n"
    NOACTUA.write(FECHA+MENSA_SERVICIO)
else:
    MENSA_SERVICIO = "No IP service available\n"
    NOACTUA.write(FECHA+MENSA_SERVICIO)
    sys.exit(1)

# Check entry into active version of the zone

COMPRUEBA_REG1 = "Checking registry "+NOMBRE
COMPRUEBA_REG2 = " an active version of the zone exists "
MENSA_ID = " , id:"+str(ZONE_ID)+"\n"
NOACTUA.write(FECHA+COMPRUEBA_REG1+COMPRUEBA_REG2+ID_ZONA+MENSA_ID)

# We assume that the current version is the latest. If not, it will not function.

REGISTRO = API.domain.zone.record.list(APIKEY, ZONE_ID, 0, {'name': NOMBRE})

if not REGISTRO:
    ACTUA.write(FECHA+"Registry doesn't exists\n")
    NOACTUA.write(FECHA+"Registry doesn't exists\n")

    VER_NUEVA = API.domain.zone.version.new(APIKEY, ZONE_ID)
    ACTUA.write(FECHA+"Creating a new version of zone: "+str(VER_NUEVA)+"\n")

    ACTUA.write(FECHA+"Activating new version\n")
    ACTIVA_NUEVA = API.domain.zone.version.set(APIKEY, ZONE_ID, VER_NUEVA)
    if ACTIVA_NUEVA:
        ACTUA.write(FECHA+ACTIVA_OK+str(ACTIVA_NUEVA)+"\n")
    else:
        ACTUA.write(FECHA+ACTIVA_KO+str(ACTIVA_NUEVA)+"\n")
        ACTUA.close()
        sys.exit(1)

    VER_ANTIGUA = VER_NUEVA - 1
    CREA_ZONA = "Creating entry "+NOMBRE+" in inactive zone "
    ACTUA.write(FECHA+CREA_ZONA+str(VER_ANTIGUA)+"\n")
    NUEVA_ENTRADA = API.domain.zone.record.add(APIKEY, ZONE_ID, VER_ANTIGUA, {'name': NOMBRE, 'type': 'A', 'value': ACTUALIP, 'ttl': int(TIEMPO_VIDA)})
    ACTUA.write(FECHA+"Created "+NUEVA_ENTRADA['name']+" registry in zone "+ZONE_NOMBRE+" , version "+str(VER_ANTIGUA)+"\n")

    ACTUA.write(FECHA+"Reactivating modified version of the zoen\n")
    ACTIVA_ANTIGUA = API.domain.zone.version.set(APIKEY, ZONE_ID, VER_ANTIGUA)
    if ACTIVA_ANTIGUA:
        ACTUA.write(FECHA+ACTIVA_OK+str(ACTIVA_NUEVA)+"\n")
    else:
        ACTUA.write(FECHA+ACTIVA_KO+str(ACTIVA_NUEVA)+"\n")
        ACTUA.close()
        sys.exit(1)

    ACTUA.write(FECHA+"Deleting temporary zone version\n")
    DELETE_NUEVA = API.domain.zone.version.delete(APIKEY, ZONE_ID, VER_NUEVA)
    if DELETE_NUEVA:
        ACTUA.write(FECHA+DELETE_OK+str(ACTIVA_NUEVA)+"\n")
        ACTUA.close()
        sys.exit(0)
    else:
        ACTUA.write(FECHA+DELETE_KO+str(ACTIVA_NUEVA)+"\n")
        ACTUA.close()
        sys.exit(1)

else:

    IP_DNS = REGISTRO[0]['value']
    IP_ACTUAL = ACTUALIP.rstrip()
    NOACTUA.write(FECHA+"Registry exists\n")
    NOACTUA.write(FECHA+"Checking for Ip change\n")
    if IP_DNS == IP_ACTUAL:
        NOACTUA.write(FECHA+"IP hasn't changed. Nothing to do\n")
        NOACTUA.close()
        sys.exit(0)
    else:
        ACTUA.write(FECHA+"IP has changed. Updating registry\n")
        VER_NUEVA = API.domain.zone.version.new(APIKEY, ZONE_ID)
        ACTUA.write(FECHA+"Creating new version of the zone: "+str(VER_NUEVA)+"\n")
        ACTUA.write(FECHA+"Activating new version\n")
        ACTIVA_NUEVA = API.domain.zone.version.set(APIKEY, ZONE_ID, VER_NUEVA)
        if ACTIVA_NUEVA:
            ACTUA.write(FECHA+ACTIVA_OK+str(ACTIVA_NUEVA)+"\n")
        else:
            ACTUA.write(FECHA+ACTIVA_KO+str(ACTIVA_NUEVA)+"\n")
            ACTUA.close()
            sys.exit(1)

        ACTUA.write(FECHA+"Updating registry in original zone\n")
        VER_ANTIGUA = VER_NUEVA - 1
        ENTRADA = API.domain.zone.record.list(APIKEY, ZONE_ID, VER_ANTIGUA, {'name': NOMBRE})
        ENTRADA_ID = ENTRADA[0]['id']
        ACTUALIZA_ENTRADA = API.domain.zone.record.update(APIKEY, ZONE_ID, VER_ANTIGUA, {'id': ENTRADA_ID}, {'name': NOMBRE, 'type': 'A', 'value': ACTUALIP, 'ttl': int(TIEMPO_VIDA)})

        ACTUA.write(FECHA+"Reactivating original zone\n")
        ACTIVA_ANTIGUA = API.domain.zone.version.set(APIKEY, ZONE_ID, VER_ANTIGUA)
        if ACTIVA_ANTIGUA:
            ACTUA.write(FECHA+ACTIVA_OK+str(ACTIVA_ANTIGUA)+"\n")
        else:
            ACTUA.write(FECHA+ACTIVA_KO+str(ACTIVA_ANTIGUA)+"\n")
            ACTUA.close()
            sys.exit(1)

        ACTUA.write(FECHA+"Removing new version\n")
        DELETE_NUEVA = API.domain.zone.version.delete(APIKEY, ZONE_ID, VER_NUEVA)
        if DELETE_NUEVA:
            ACTUA.write(FECHA+DELETE_OK+str(DELETE_NUEVA)+"\n")
            ACTUA.write(FECHA+"Registry entry "+NOMBRE+" with values:\n"+FECHA+"Name: "+ACTUALIZA_ENTRADA[0]['name']+"\n"+FECHA+"IP: "+ACTUALIZA_ENTRADA[0]['value']+"\n"+FECHA+"DNS Registry Type: "+ACTUALIZA_ENTRADA[0]['type']+"\n"+FECHA+"TTL: "+str(ACTUALIZA_ENTRADA[0]['ttl'])+" has been updated\n")
            ACTUA.close()
            sys.exit(0)
        else:
            ACTUA.write(FECHA+DELETE_KO+str(DELETE_NUEVA)+"\n")
            ACTUA.close()
            sys.exit(1)
