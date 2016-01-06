#!/usr/bin/env python3

import argparse
import os
import serial as pyserial
import signal
import sys
import yaml
import messages

import time

def cli_opts():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--homeassistant-config",
        type=str,
        required=False,
        dest="config",
        help="Create configuration section for home assistant",)
    parser.add_argument('device')

    return parser.parse_args()

def add_device(devices, scsID, haID, name):
    if scsID in devices:
        return

    devices[scsID] = {
        haID: {
            'name': name,
            'scs_id': scsID
        }
    }

def home_assistant_config(devices):
    d = {}
    for k,v in devices.items():
        for k2, v2 in v.items():
            d[k2] = v2

    config = {
        'switch': {
            'platform': 'scsgate',
            'devices': d
        }
    }
    return config

def signal_handler(signum, frame):
    if options.config:
        with open(options.config, "w") as cfg:
            yaml.dump(home_assistant_config(devices), cfg)
            print("Dumped home assistant configuration at", options.config)
    sys.exit(0)

def setup_signal_handler():
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGQUIT, signal_handler)

setup_signal_handler()

options = cli_opts()
devices = {}

serial = pyserial.Serial(options.device, 115200)

print("Enabling ASCII mode")
serial.write(b"@MA")
print(serial.read(1))

print("Entering monitoring mode, press CTRL-C to quit")

while True:
    serial.write(b"@R")
    length = int(serial.read())
    data = serial.read(length * 2)
    message = messages.parse(data)
    print(message)
    if not options.config or message.entity is None or message.entity in devices:
        continue

    print("New device found")
    haID = input("Enter home assistant unique ID: ")
    name = input("Enter name: ")
    add_device(devices=devices,scsID=message.entity, haID=haID, name=name)
