import serial as pyserial

class Connection:
    """ Connection to SCSGate device """

    def __init__(self, device, logger):
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
        return self._serial

    def close(self):
        self._serial.write(b"@c")
        self._serial.read()
        self._serial.close()
