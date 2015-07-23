"""
config file for bcollector scripts
"""

import os


PROCESSES = 4 # number of processes for multiprocessing

DATADIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
LOGFILE = None

COMMANDS = [
    ['portlogdump', 'portlogdump'],
]

CONNECTIONS = [
   #['switch name', 'switch address', 'username', 'password', COMMANDS],
]
