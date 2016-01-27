""" This module contains all the possible messages to send via
scsgate.Reactor """

from scsgate.messages import compose_telegram, parse, StateMessage


class ExecutionError(BaseException):
    """ Error raised when something goes wrong while executing a task """
    pass


class BasicTask:
    """ Basic task, not to be used directly """

    def execute(self, connection):
        """ Method to be implemented by all subclasses """
        raise NotImplementedError()


class MonitorTask(BasicTask):
    """ Read the buffer and invokes the notification endpoint if there's
        a relevant message """

    def __init__(self, notification_endpoint):
        self._notification_endpoint = notification_endpoint
        self._last_raw_state_message = None

    def execute(self, connection):
        connection.serial.write(b"@r")
        length = int(connection.serial.read(), 16)
        if length == 0:
            return
        data = connection.serial.read(length * 2)
        message = parse(data)
        # Filter duplicated state messages. The filtering feature
        # of SCSGate is buggy and causes @r to always return 0 available
        # messages
        if isinstance(message, StateMessage):
            if self._last_raw_state_message == data:
                return
            else:
                self._last_raw_state_message = data
        self._notification_endpoint(message)

    def __str__(self):
        return "Monitor Task"


class SetStatusTask(BasicTask):
    """ Generic task to request a status change. To not be used directly """

    def __init__(self, target, action):
        self._target = target
        self._action = action

    def execute(self, connection):
        command = "@w{action}{target}".format(
            action=self._action,
            target=self._target)

        connection.serial.write(str.encode(command))
        ret = connection.serial.read()
        if ret != b'k':
            raise ExecutionError(
                "Error while setting status. Command {}, got {}".format(
                    command, ret))

    def __str__(self):
        return "SetStatusTask: target {} - action {}".format(
            self._target, self._action)


class ToggleStatusTask(SetStatusTask):
    """ Change the toggled status of a light or switch """

    def __init__(self, target, toggled):
        self._toggled = toggled
        action = 1
        if toggled:
            action = 0

        SetStatusTask.__init__(
            self,
            target=target,
            action=action)

    def __str__(self):
        return "ToggleStatusTask: target {} - toggled {}".format(
            self._target, self._toggled)


class RaiseRollerShutterTask(SetStatusTask):
    """ Raise a roller shutter """

    def __init__(self, target):
        SetStatusTask.__init__(
            self,
            target=target,
            action=8)

    def __str__(self):
        return "RaiseRollerShutterTask: target {}".format(
            self._target)


class LowerRollerShutterTask(SetStatusTask):
    """ Lower a roller shutter """

    def __init__(self, target):
        SetStatusTask.__init__(
            self,
            target=target,
            action=9)

    def __str__(self):
        return "LowerRollerShutterTask: target {}".format(
            self._target)


class HaltRollerShutterTask(SetStatusTask):
    """ Halt a roller shutter """

    def __init__(self, target):
        SetStatusTask.__init__(
            self,
            target=target,
            action="A")

    def __str__(self):
        return "HaltRollerShutterTask: target {}".format(
            self._target)


class GetStatusTask(BasicTask):
    """ Requests the current status of a device """

    def __init__(self, target):
        self._target = target

    def execute(self, connection):
        command = b"@W7" + compose_telegram([
            str.encode(self._target),
            b"00",
            b"15",
            b"00"])
        connection.serial.write(command)
        ret = connection.serial.read()
        if ret != b'k':
            raise ExecutionError(
                "Error while requesting status. Command {}, got {}".format(
                    command, ret))

    def __str__(self):
        return "GetStatusTask: target {}".format(
            self._target)
