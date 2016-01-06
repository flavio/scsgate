class SCSMessage:
    """ Base class for all SCS messages """

    @property
    def data(self):
        return "".join(self._data)

    @property
    def source(self):
        return self._source

    @property
    def status(self):
        return self._status

    @property
    def entity(self):
        """ Return the "main character" of the message """
        return None

class AckMessage(SCSMessage):
    """ Ack message """

    def __repr__(self):
        return "AckMessage()"

    def __str__(self):
        return "AckMessage"

class UnknownMessage(SCSMessage):
    """ Message unknown """

    def __init__(self, data):
        self._data = data

    def __repr__(self):
        return "UnknownMessage()"

    def __str__(self):
        return "UnknownMessage: {0}".format(self._data)

class StateMessage(SCSMessage):
    """ Message issued to notify a change of state """

    def __init__(self, data):
        self._data = data
        self._source = data[2]
        self._status = "off"
        if data[4] == "00":
            self._status = "on"

    def __repr__(self):
        return "StateMessage()"

    def __str__(self):
        return "StateMessage: source {source} - status {status} - raw: {raw}".format(
                source=self._source,
                status=self._status,
                raw=self._data)

    @property
    def entity(self):
        return self._source

class CommandMessage(SCSMessage):
    """ Message issued to turn on/off a switch """

    def __init__(self, data):
        self._data = data
        self._destination = data[1]
        self._source = data[2]
        self._status = "off"
        if data[4] == "00":
            self._status = "on"

    @property
    def destination(self):
        return self._destination

    @property
    def entity(self):
        return self._destination

    def __repr__(self):
        return "CommandMessage()"

    def __str__(self):
        return "CommandMessage: destination {destination} - source {source} - status {status} - raw: {raw}".format(
                source=self._source,
                status=self._status,
                raw=self._data,
                destination=self._destination)

class RequestStatusMessage(SCSMessage):
    """ Message sent to request the status of a switch """

    def __init__(self, data):
        self._data = data
        self._destination = data[1]
        self._source = data[2]

    @property
    def destination(self):
        return self._destination

    @property
    def entity(self):
        return self._destination

    def __repr__(self):
        return "RequestStatusMessage()"

    def __str__(self):
        return "RequestStatusMessage: destination {destination} - source {source} - raw: {raw}".format(
                source=self._source,
                raw=self._data,
                _destination=self._destination)

def parse(data):
    """ Parses a raw datagram and return the right type of message """

    # convert to string
    data = data.decode("ascii")

    if len(data) == 2 and data == "A5":
        return AckMessage()

    # split into bytes
    bytes = [data[i:i+2] for i in range(len(data)) if i % 2 == 0]

    if len(bytes) != 7:
        return UnknownMessage(bytes)

    if bytes[1] == "B8":
        return StateMessage(bytes)
    elif bytes[3] == "12":
        return CommandMessage(bytes)
    elif bytes[3] == "15":
        return RequestStatusMessage(bytes)
    else:
        return UnknownMessage(bytes)
