#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
 Woodlouse v2.0NeXTGen

  No-IP type script for the provider Gandi.net

  Sergio Fernandez Cordero <sergio@fernandezcordero.net>
  twitter: http: //twitter.com/elautoestopista
  http://www.fernandezcordero.net/blog

  License GPLv3 - https://www.gnu.org/copyleft/gpl.html - see LICENSE for details

  CHANGELOG:
  ----------
      - Refactor for Python3.X
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

import xmlrpc
import sys
import datetime
import os
import requests
import time

# If no arguments, and use the program banner is received
# We define the messages that build exits

MENSA_BANNER = "Woodlouse v2.0 NeXTGen - Sergio Fernández Cordero 2016\n"
MENSA_LICEN = "This program is distributed with GPLv3 license - https://www.gnu.org/copyleft/gpl.html .\n"
MENSA_USO = "\nUsage: python woodlouse.py"
CONF_ERROR = "Configuration file config.py not found"
ERROR_ARG = "Error: No arguments accepted. Please use config.py\n"
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


#Useful Functions
def log_noactua(msg):
    try:
        noactua = open(DIR_OPERACIONES, "a")
        noactua.write(msg)
        noactua.close()
    except OSError:
        print("Error while logging")
        sys.exit(1)


def log_actua(msg):
    try:
        actua = open(DIRCAMBIOS, "a")  # "a" includes writing if the file does not exist
        actua.write(msg)
        actua.close()
    except OSError:
        print("Error while logging")
        sys.exit(1)


# Check for config.py file
try:
    from config import config
except FileNotFoundError:
    print(MENSA_BANNER + CONF_ERROR)
    sys.exit(1)

# Locate the current working path, where it is the script
RUTA = sys.path[0]

# Check that last argument as TTL is an integer
# Then we will turn to type int

# TTL. st your discrection

try:
    if isinstance(config.get('TTL'), int):
        TIEMPO_VIDA = config.get('TTL')
except TypeError:
    print(ERROR_TTL)
    sys.exit(1)

# Assign the input arguments
# The area that you have assigned to your domain.
# If the area is used by multiple domains, registration
# Will be created in all of them.

try:
    if isinstance(config.get('ZONE'), str):
        ID_ZONA = config.get('ZONE')
except TypeError:
    print(ERROR_ZONA_CADENA)
    sys.exit(1)

# Name of the record that we want to create
# (Do not put the domain name back, it's automatically added)
try:
    if isinstance(config.get('REGISTRY'), str):
        NOMBRE = config.get('ZONE')
except TypeError:
    print(ERROR_REGISTRO_CADENA)
    sys.exit(1)

# API key
# Check that you have 24 characters without spaces
try:
    if len(config.get('APIKEY')) == 24 and not (' ' in config.get('APIKEY')):
        APIKEY = config.get('APIKEY')
except ValueError:
    print(ERROR_API)
    sys.exit(1)

# Environment: Production o Test (OT&E)
try:
    if config.get('ZONE') == "prod" or config.get('ZONE') == "test":
        ENTORNO = config.get('ZONE')
        # Check environment is PROD or TEST
        if ENTORNO == "prod":
            # Load the API Gandi.net
            # Production environment
            API = xmlrpc.client.ServerProxy('https://rpc.gandi.net/xmlrpc/')
        elif ENTORNO == "test":
            # Test environment(OT&E)
            API = xmlrpc.client.ServerProxy('https://rpc.ote.gandi.net/xmlrpc/')
        else:
            API = "Null"
except ValueError:
    print(ERROR_ENV)
    sys.exit(1)


# Initial definitions
try:
    ZONA = API.domain.zone.list(APIKEY, {'name': ID_ZONA})
    if not ZONA:
        print("Zone " + ID_ZONA + " doesn't exists")
        sys.exit(1)
    else:
        ZONE_ID = ZONA[0]['id']
        ZONE_NOMBRE = ZONA[0]['name']
except NameError:
    print(ERROR_API)
    sys.exit(1)

# We define the date and time of execution

MOMENTO = datetime.datetime.now()
FECHA = MOMENTO.strftime('%d %b %Y %H:%M - ')

# We define the log files
# Check that the directory exists logs

# We build the paths to the log files.
try:
    os.path.isdir(config.get('LOGS'))
    DIR_RUTA = config.get('LOGS')
except FileNotFoundError:
    print(ERROR_LOGDIR)
    DIR_RUTA = RUTA + config.get('LOGS')
    os.mkdir(DIR_RUTA)

# The file where the last execution are stored always overwrites
DIR_OPERACIONES = DIR_RUTA + "operations.log"
# The file where the changes are stored only be created if there
# If it exists, the new data will be added at the end
DIRCAMBIOS = DIR_RUTA + "changes.log"

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
try:
    IP_RESOURCE = ip_publica()
except ValueError:
    MENSA_SERVICIO = "No IP service available\n"
    log_noactua(FECHA + MENSA_SERVICIO)
try:
    RECURSO, ACTUALIP = IP_RESOURCE
    MENSA_SERVICIO = "Using service" + RECURSO + " get IP " + ACTUALIP + "\n"
    COMPRUEBA_REG1 = "Checking registry " + NOMBRE
    COMPRUEBA_REG2 = " an active version of the zone exists "
    MENSA_ID = " , id:" + str(ZONE_ID) + "\n"
    log_noactua(FECHA + MENSA_SERVICIO)
    log_noactua(FECHA + COMPRUEBA_REG1 + COMPRUEBA_REG2 + ID_ZONA + MENSA_ID)
except ConnectionError:
    MENSA_SERVICIO = "Service " + RECURSO + "unavailable"
    log_noactua(FECHA + MENSA_SERVICIO)


# We assume that the current version is the latest. If not, it will not function.

try:
    REGISTRO = API.domain.zone.record.list(APIKEY, ZONE_ID, 0, {'name': NOMBRE})
    IP_DNS = REGISTRO[0]['value']
    IP_ACTUAL = ACTUALIP.rstrip()
    log_noactua(FECHA + "Registry exists\n")
    log_noactua(FECHA + "Checking for Ip change\n")
    if IP_DNS == IP_ACTUAL:
        log_noactua(FECHA + "IP hasn't changed. Nothing to do\n")
        sys.exit(0)
    else:
        log_actua(FECHA + "IP has changed. Updating registry\n")
        VER_NUEVA = API.domain.zone.version.new(APIKEY, ZONE_ID)
        log_actua(FECHA + "Creating new version of the zone: " + str(VER_NUEVA) + "\n")
        log_actua(FECHA + "Activating new version\n")
        ACTIVA_NUEVA = API.domain.zone.version.set(APIKEY, ZONE_ID, VER_NUEVA)
        if ACTIVA_NUEVA:
            log_actua(FECHA + ACTIVA_OK + str(ACTIVA_NUEVA) + "\n")
        else:
            log_actua(FECHA + ACTIVA_KO + str(ACTIVA_NUEVA) + "\n")
            sys.exit(1)

        log_actua(FECHA + "Updating registry in original zone\n")
        VER_ANTIGUA = VER_NUEVA - 1
        ENTRADA = API.domain.zone.record.list(APIKEY, ZONE_ID, VER_ANTIGUA, {'name': NOMBRE})
        ENTRADA_ID = ENTRADA[0]['id']
        ACTUALIZA_ENTRADA = API.domain.zone.record.update(APIKEY, ZONE_ID, VER_ANTIGUA, {'id': ENTRADA_ID},
                                                          {'name': NOMBRE, 'type': 'A', 'value': ACTUALIP,
                                                           'ttl': int(TIEMPO_VIDA)})

        log_actua(FECHA + "Reactivating original zone\n")
        ACTIVA_ANTIGUA = API.domain.zone.version.set(APIKEY, ZONE_ID, VER_ANTIGUA)
        if ACTIVA_ANTIGUA:
            log_actua(FECHA + ACTIVA_OK + str(ACTIVA_ANTIGUA) + "\n")
        else:
            log_actua(FECHA + ACTIVA_KO + str(ACTIVA_ANTIGUA) + "\n")
            sys.exit(1)

        log_actua(FECHA + "Removing new version\n")
        DELETE_NUEVA = API.domain.zone.version.delete(APIKEY, ZONE_ID, VER_NUEVA)
        if DELETE_NUEVA:
            log_actua(FECHA + DELETE_OK + str(DELETE_NUEVA) + "\n")
            log_actua(
                FECHA + "Registry entry " + NOMBRE + " with values:\n" + FECHA + "Name: " + ACTUALIZA_ENTRADA[0][
                    'name'] + "\n" + FECHA + "IP: " + ACTUALIZA_ENTRADA[0][
                    'value'] + "\n" + FECHA + "DNS Registry Type: " + ACTUALIZA_ENTRADA[0][
                    'type'] + "\n" + FECHA + "TTL: " + str(ACTUALIZA_ENTRADA[0]['ttl']) + " has been updated\n")
            sys.exit(0)
        else:
            log_actua(FECHA + DELETE_KO + str(DELETE_NUEVA) + "\n")
            sys.exit(1)
except ReferenceError:
    log_actua(FECHA + "Registry doesn't exists\n")
    log_noactua(FECHA + "Registry doesn't exists\n")

    VER_NUEVA = API.domain.zone.version.new(APIKEY, ZONE_ID)
    log_actua(FECHA + "Creating a new version of zone: " + str(VER_NUEVA) + "\n")

    log_actua(FECHA + "Activating new version\n")
    ACTIVA_NUEVA = API.domain.zone.version.set(APIKEY, ZONE_ID, VER_NUEVA)
    if ACTIVA_NUEVA:
        log_actua(FECHA + ACTIVA_OK + str(ACTIVA_NUEVA) + "\n")
    else:
        log_actua(FECHA + ACTIVA_KO + str(ACTIVA_NUEVA) + "\n")
        sys.exit(1)

    VER_ANTIGUA = VER_NUEVA - 1
    CREA_ZONA = "Creating entry " + NOMBRE + " in inactive zone "
    log_actua(FECHA + CREA_ZONA + str(VER_ANTIGUA) + "\n")
    NUEVA_ENTRADA = API.domain.zone.record.add(APIKEY, ZONE_ID, VER_ANTIGUA,
                                               {'name': NOMBRE, 'type': 'A', 'value': ACTUALIP,
                                                'ttl': int(TIEMPO_VIDA)})
    log_actua(FECHA + "Created " + NUEVA_ENTRADA['name'] + " registry in zone " + ZONE_NOMBRE + " , version " + str(
        VER_ANTIGUA) + "\n")

    log_actua(FECHA + "Reactivating modified version of the zoen\n")
    ACTIVA_ANTIGUA = API.domain.zone.version.set(APIKEY, ZONE_ID, VER_ANTIGUA)
    if ACTIVA_ANTIGUA:
        log_actua(FECHA + ACTIVA_OK + str(ACTIVA_NUEVA) + "\n")
    else:
        log_actua(FECHA + ACTIVA_KO + str(ACTIVA_NUEVA) + "\n")
        sys.exit(1)

    log_actua(FECHA + "Deleting temporary zone version\n")
    DELETE_NUEVA = API.domain.zone.version.delete(APIKEY, ZONE_ID, VER_NUEVA)
    if DELETE_NUEVA:
        log_actua(FECHA + DELETE_OK + str(ACTIVA_NUEVA) + "\n")
        sys.exit(0)
    else:
        log_actua(FECHA + DELETE_KO + str(ACTIVA_NUEVA) + "\n")
        sys.exit(1)
