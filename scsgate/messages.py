""" This module contains the definition of all the messages known by
SCSGate """

from functools import reduce


class SCSMessage:
    """ Base class for all SCS messages """
    def __init__(self, data):
        self._data = data

    @property
    def bytes(self):
        """ A list containing all the bytes of the message """
        return self._data

    @property
    def data(self):
        """ The raw message """
        return "".join(self._data)

    @property
    def entity(self):
        """ The ID of the subject of this message """
        return None


class AckMessage(SCSMessage):
    """ Ack message """

    def __init__(self):
        SCSMessage.__init__(self, "")

    def __repr__(self):
        return "AckMessage()"

    def __str__(self):
        return "AckMessage"


class UnknownMessage(SCSMessage):
    """ Message unknown """

    def __init__(self, data):
        SCSMessage.__init__(self, data)

    def __repr__(self):
        return "UnknownMessage()"

    def __str__(self):
        return "UnknownMessage: {0}".format(self._data)


class StateMessage(SCSMessage):
    """ Message issued to notify a change of state """

    def __init__(self, data):
        SCSMessage.__init__(self, data)
        self._source = data[2]
        self._status = "off"
        if data[4] == "00":
            self._status = "on"

    def __repr__(self):
        return "StateMessage()"

    def __str__(self):
        return "StateMessage: source {src} - status {status} - raw: {raw}".format(
            src=self._source,
            status=self._status,
            raw=self._data)

    @property
    def toggled(self):
        """ True if the light is toggled, False otherwise """
        return self._status == "on"

    @property
    def source(self):
        """ The source of the message """
        return self._source

    @property
    def status(self):
        """ Current status """
        return self._status

    @property
    def entity(self):
        """ The ID of the subject of this message """
        return self._source


class CommandMessage(SCSMessage):
    """ Message issued to turn on/off a switch """

    def __init__(self, data):
        SCSMessage.__init__(self, data)
        self._destination = data[1]
        self._source = data[2]
        self._status = "off"
        if data[4] == "00":
            self._status = "on"

    @property
    def destination(self):
        """ The target of the message """
        return self._destination

    @property
    def entity(self):
        """ The ID of the subject of this message """
        return self._destination

    @property
    def source(self):
        """ The source of the message """
        return self._source

    @property
    def status(self):
        """ Current status """
        return self._status

    def __repr__(self):
        return "CommandMessage()"

    def __str__(self):
        message = "CommandMessage: destination {dest} - source {src} - status {status} - raw: {raw}"

        return message.format(
            src=self._source,
            status=self._status,
            raw=self._data,
            dest=self._destination)


class ScenarioTriggeredMessage(SCSMessage):
    """ Message issued when a scenario switch is pressed """

    def __init__(self, data):
        SCSMessage.__init__(self, data)
        self._source = data[1]
        self._scenario = data[4]

    @property
    def scenario(self):
        """ The scenario ID """
        return self._scenario

    @property
    def entity(self):
        """ The ID of the subject of this message """
        return self._source

    @property
    def source(self):
        """ The source of the message """
        return self._source

    def __repr__(self):
        return "ScenarioTriggeredMessage()"

    def __str__(self):
        message = "ScenarioTriggeredMessage: source {src} - scenario {scen} - raw: {raw}"

        return message.format(
            src=self._source,
            raw=self._data,
            scen=self._scenario)


class RequestStatusMessage(SCSMessage):
    """ Message sent to request the status of a switch """

    def __init__(self, data):
        SCSMessage.__init__(self, data)
        self._destination = data[1]
        self._source = data[2]

    @property
    def destination(self):
        """ The target of the message """
        return self._destination

    @property
    def entity(self):
        """ The ID of the subject of this message """
        return self._destination

    @property
    def source(self):
        """ The source of the message """
        return self._source

    def __repr__(self):
        return "RequestStatusMessage()"

    def __str__(self):
        return "RequestStatusMessage: destination {dest} - source {src} - raw: {raw}".format(
            src=self._source,
            raw=self._data,
            dest=self._destination)


def parse(data):
    """ Parses a raw datagram and return the right type of message """

    # convert to string
    data = data.decode("ascii")

    if len(data) == 2 and data == "A5":
        return AckMessage()

    # split into bytes
    raw = [data[i:i+2] for i in range(len(data)) if i % 2 == 0]

    if len(raw) != 7:
        return UnknownMessage(raw)

    if raw[1] == "B8":
        return StateMessage(raw)
    elif raw[3] == "12":
        return CommandMessage(raw)
    elif raw[3] == "14":
        return ScenarioTriggeredMessage(raw)
    elif raw[3] == "15":
        return RequestStatusMessage(raw)
    else:
        return UnknownMessage(raw)


def checksum_bytes(data):
    """ Returns a XOR of all the bytes specified inside of the given list """

    int_values = [int(x, 16) for x in data]
    int_xor = reduce(lambda x, y: x ^ y, int_values)
    hex_xor = "{:X}".format(int_xor)
    if len(hex_xor) % 2 != 0:
        hex_xor = "0" + hex_xor

    return str.encode(hex_xor)


def compose_telegram(body):
    """ Compose a SCS message

        body: list containing the body of the message.
        returns: full telegram expressed (bytes instance)
    """

    msg = [b"A8"] + body + [checksum_bytes(body)] + [b"A3"]
    return str.encode("".join([x.decode() for x in msg]))
