""" This module implements the scs-monitor cli tool """
import argparse
import logging
import pathlib
import signal
import sys
import yaml

import scsgate.messages as messages
from scsgate.connection import Connection


def cli_opts():
    """ Handle the command line options """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--homeassistant-config",
        type=str,
        required=False,
        dest="config",
        help="Create configuration section for home assistant",)
    parser.add_argument(
        "-f",
        "--filter",
        type=str,
        required=False,
        dest="filter",
        help="Ignore events related with these devices",)
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        dest="output",
        help="Send output to file",)
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

        # A dict with scs_id as key and another dict as value.
        # The latter dict has 'ha_id' and 'name' as keys.
        self._devices = {}

        log_level = logging.WARNING

        if options.output:
            logging.basicConfig(
                format='%(asctime)s : %(message)s',
                level=logging.DEBUG,
                filename=options.output,
                filemode="a")
        else:
            logging.basicConfig(
                format='%(asctime)s : %(message)s',
                level=logging.DEBUG)

        if options.verbose:
            log_level = logging.DEBUG
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s: %(message)s',
            level=log_level)

        if self._options.filter:
            self._load_filter(self._options.filter)

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
                print(
                    "Dumped home assistant configuration at",
                    self._options.config)
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
            if not (self._options.filter and
                    message.entity and
                    message.entity in self._devices):
                logging.debug(" ".join(message.bytes))
            if not self._options.config or \
               message.entity is None or \
               message.entity in self._devices:
                continue

            print("New device found")
            ha_id = input("Enter home assistant unique ID: ")
            name = input("Enter name: ")
            self._add_device(scs_id=message.entity, ha_id=ha_id, name=name)

    def _add_device(self, scs_id, ha_id, name):
        """ Add device to the list of known ones """
        if scs_id in self._devices:
            return

        self._devices[scs_id] = {
            'name': name,
            'ha_id': ha_id
        }

    def _home_assistant_config(self):
        """ Creates home assistant configuration for the known devices """
        devices = {}
        for scs_id, dev in self._devices.items():
            devices[dev['ha_id']] = {
                'name': dev['name'],
                'scs_id': scs_id}

        return {'devices': devices}

    def _load_filter(self, config):
        """ Load the filter file and populates self._devices accordingly """
        path = pathlib.Path(config)
        if not path.is_file():
            return

        with open(config, 'r') as conf:
            devices = yaml.load(conf)['devices']
            for ha_id, dev in devices.items():
                self._devices[dev['scs_id']] = {
                    ha_id: dev,
                    'name': dev['name']}


def main():
    """ Entry point of the scs-monitor cli tool """

    options = cli_opts()
    monitor = Monitor(options)
    monitor.start()
