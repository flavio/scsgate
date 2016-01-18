from scsgate.messages import checksum_bytes, parse, StateMessage

class ExecutionError(BaseException):
    pass

class BasicTask:

    def __init__(self, serial, logger):
        self._serial = serial
        self._logger = logger

    def execute(self):
        raise NotImplementedError()


class MonitorTask(BasicTask):

    def __init__(self, logger, serial, notification_endpoint):
        BasicTask.__init__(self, serial, logger)
        self._notification_endpoint = notification_endpoint
        self._last_raw_state_message = None

    def execute(self):
        self._serial.write(b"@r")
        length = int(self._serial.read(), 16)
        if length == 0:
            return
        data = self._serial.read(length * 2)
        message = parse(data)
        # Filter duplicated state messages. The filtering feature
        # of SCSGate is buggy and causes @r to always return 0 available
        # messages
        if isinstance(message, StateMessage):
            if self._last_raw_state_message == data:
                self._logger.debug("Monitoring task: ignoring duplicated state message")
                return
            else:
                self._last_raw_state_message = data
        self._logger.debug("Monitoring task: got message")
        self._notification_endpoint(message)

    def __str__(self):
        return "Monitor Task"


class SetStatusTask(BasicTask):

    def __init__(self, logger, serial, target, action):
        BasicTask.__init__(self, serial, logger)
        self._target = target
        self._action = action

    def execute(self):
        command = "@w{action}{target}".format(
                action=self._action,
                target=self._target)

        self._serial.write(str.encode(command))
        ret = self._serial.read()
        if ret != b'k':
            raise ExecutionError("Error while setting status. Command {}, got {}".format(command, ret))

    def __str__(self):
        return "SetStatusTask: target {} - action {}".format(
                self._target, self._action)

class ToggleStatusTask(SetStatusTask):
    def __init__(self, logger, serial, target, toggled):
        self._toggled = toggled
        action = 1
        if toggled:
            action = 0

        SetStatusTask.__init__(
                self,
                target=target,
                serial=serial,
                logger=logger,
                action=action)

    def __str__(self):
        return "ToggleStatusTask: target {} - toggled {}".format(
                self._target, self._toggled)

class RaiseRollerShutterTask(SetStatusTask):
    def __init__(self, logger, serial, target):
        SetStatusTask.__init__(
                self,
                target=target,
                serial=serial,
                logger=logger,
                action=8)

    def __str__(self):
        return "RaiseRollerShutterTask: target {}".format(
                self._target)

class LowerRollerShutterTask(SetStatusTask):
    def __init__(self, logger, serial, target):
        SetStatusTask.__init__(
                self,
                target=target,
                serial=serial,
                logger=logger,
                action=9)

    def __str__(self):
        return "LowerRollerShutterTask: target {}".format(
                self._target)

class HaltRollerShutterTask(SetStatusTask):
    def __init__(self, logger, serial, target):
        SetStatusTask.__init__(
                self,
                target=target,
                serial=serial,
                logger=logger,
                action="A")

    def __str__(self):
        return "HaltRollerShutterTask: target {}".format(
                self._target)

class GetStatusTask(BasicTask):

    def __init__(self, logger, serial, target):
        BasicTask.__init__(self, serial, logger)
        self._target = target

    def execute(self):
        command = b"@W7" + self.telegram()
        self._serial.write(command)
        ret = self._serial.read()
        if ret != b'k':
            raise ExecutionError("Error while requesting status. Command {}, got {}".format(command, ret))
        self._logger.debug("Successfully requested status for device {}".format(self._target))

    def telegram(self):
        msg = [
                str.encode(self._target),
                b"00",
                b"15",
                b"00"]
        msg.append(checksum_bytes(msg))
        ret = [b"A8"] + msg + [b"A3"]
        return str.encode("".join([x.decode() for x in ret]))

    def __str__(self):
        return "GetStatusTask: target {}".format(
                self._target)
