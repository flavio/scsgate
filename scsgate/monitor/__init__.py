import argparse
import logging
import os
import signal
import sys
import yaml

import scsgate.messages as messages
from scsgate.connection import Connection

def cli_opts():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--homeassistant-config",
        type=str,
        required=False,
        dest="config",
        help="Create configuration section for home assistant",)
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        dest="verbose",
        help="Verbose output",)
    parser.add_argument('device')

    return parser.parse_args()

class Monitor:
    """ Class monitoring bus event """

    def __init__(self, options):
        self._options = options
        self._devices = {}

        logLevel = logging.WARNING
        if options.verbose:
            logLevel = logging.DEBUG
        logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logLevel)

        self._connection = Connection(device=options.device, logger=logging)

        self._setup_signal_handler()

    def _setup_signal_handler(self):
        """ Register signal handlers """
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGQUIT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """ Method called when handling signals """
        if self._options.config:
            with open(self._options.config, "w") as cfg:
                yaml.dump(self._home_assistant_config(), cfg)
                print("Dumped home assistant configuration at", self._options.config)
        self._connection.close()
        sys.exit(0)

    def start(self):
        """ Monitor the bus for events and handle them """
        print("Entering monitoring mode, press CTRL-C to quit")
        serial = self._connection.serial

        while True:
            serial.write(b"@R")
            length = int(serial.read(), 16)
            data = serial.read(length * 2)
            message = messages.parse(data)
            print(message)
            if not self._options.config or message.entity is None or message.entity in self._devices:
                continue

            print("New device found")
            haID = input("Enter home assistant unique ID: ")
            name = input("Enter name: ")
            self._add_device(scsID=message.entity, haID=haID, name=name)

    def _add_device(self, scsID, haID, name):
        """ Add device to the list of known ones """
        if scsID in self._devices:
            return

        self._devices[scsID] = {
            haID: {
                'name': name,
                'scs_id': scsID
            }
        }

    def _home_assistant_config(self):
        """ Creates home assistant configuration for the known devices """
        d = {}
        for k,v in self._devices.items():
            for k2, v2 in v.items():
                d[k2] = v2

        config = {
            'switch': {
                'platform': 'scsgate',
                'devices': d
            }
        }
        return config

def main():
    """ Entry point of the scsmonitor cli tool """

    options = cli_opts()
    monitor = Monitor(options)
    monitor.start()
