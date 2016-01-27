""" This module contains an helper class to initiate a connection
with the SCSGate device """

import serial as pyserial


class Connection:
    """ Connection to SCSGate device """

    def __init__(self, device, logger):
        """ Initialize the class

        Arguments:
        device: string containing the serial device allocated to SCSGate
        logger: instance of logging
        """
        self._serial = pyserial.Serial(device, 115200)

        logger.info("Clearing buffers")
        self._serial.write(b"@b")
        ret = self._serial.read(1)
        if ret != b"k":
            raise RuntimeError("Error while clearing buffers")

        # ensure pending operations are terminated (eg: @r, @l)
        self._serial.write(b"@c")
        ret = self._serial.read()
        if ret != b"k":
            raise RuntimeError("Error while cancelling pending operations")

        logger.info("Enabling ASCII mode")
        self._serial.write(b"@MA")
        ret = self._serial.read(1)
        if ret != b"k":
            raise RuntimeError("Error while enabling ASCII mode")

        logger.info("Filter Ack messages")
        self._serial.write(b"@F2")
        ret = self._serial.read(1)
        if ret != b"k":
            raise RuntimeError("Error while setting filter")

    @property
    def serial(self):
        """ Returns the pyserial.Serial instance """
        return self._serial

    def close(self):
        """ Closes the connection to the serial port and ensure no pending
        operatoin are left """
        self._serial.write(b"@c")
        self._serial.read()
        self._serial.close()
