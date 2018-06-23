""" This module contains an helper class to initiate a connection
with the SCSGate device """

import serial as pyserial
import socket
class Connection:

    """ Connection to SCSGate device """

    def __init__(self, device, logger, port):
        """ Initialize the class

        Arguments:
        device: string containing the serial device allocated to SCSGate
        logger: instance of logging
        """
        self.device = device
        self.logger = logger
        self.port = port
        if port != 0:
            try:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._socket.settimeout(1)
            except socket.error:
                raise RuntimeError("Failed to create sockt")
        else:
            self._socket = pyserial.Serial(device, 115200)

        logger.info("Clearing buffers")
        self.send(b"@b")
        ret = self.receive()
        if (ret != b"k") or (ret is None):
            raise RuntimeError("Error while clearing buffers")

        # ensure pending operations are terminated (eg: @r, @l)
        self.send(b"@c")
        ret = self.receive()
        if (ret != b"k") or (ret is None):
            raise RuntimeError("Error while cancelling pending operations")

        logger.info("Enabling ASCII mode")
        self.send(b"@MA")
        ret = self.receive()
        if (ret != b"k") or (ret is None):
            raise RuntimeError("Error while enabling ASCII mode")

        logger.info("Filter Ack messages")
        self.send(b"@F2")
        ret = self.receive()
        if (ret != b"k") or (ret is None):
            raise RuntimeError("Error while setting filter")

    @property
    def close(self):
        """ Closes the connection to the serial port and ensure no pending
        operatoin are left """
        self.send(b"@c")
        self.receive()
        self._socket.close()

    def send(self, message):
        if self.port != 0:
            self._socket.sendto(message, (self.device, self.port))
        else:
            self._socket.write(message)

    def receive(self):
        ret = None
        if self.port != 0:
            try:    
                ret = self._socket.recvfrom(1024);
            except socket.timeout:
                self.logger.info("Socket Timeout")
                return
        else:
            lenght = int(self._socket.read(), 16)
            if lenght == b'k':
                return lenght
            else:
                data = self._socket.read(lenght * 2)
                return lenght + data
        return ret[0]
