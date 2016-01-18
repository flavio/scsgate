import enum
import queue
import threading

from scsgate.tasks import *
import scsgate.connection

class Connector(threading.Thread):

    def __init__(self, connection, handle_message, logger=None):
        threading.Thread.__init__(self)
        self._connection = connection
        self._handle_message = handle_message
        self._terminate = False
        self._logger = logger
        self._request_queue = queue.Queue()

    def run(self):
        task = None
        monitor_task = MonitorTask(
            logger=self._logger,
            serial=self._connection.serial,
            notification_endpoint=self._handle_message)

        while True:
            if self._terminate:
                self._logger.info("scsgate.Connector thread exiting")
                self._connection.close()
                break
            try:
                task = self._request_queue.get_nowait()
                self._logger.info("scsgate.Connector: got task {}".format(task))
            except queue.Empty:
                task = monitor_task

            try:
                task.execute()
            except ExecutionError as e:
                self._logger.error(e)

    def stop(self):
        self._terminate = True

    def request_status(self, target):
        t = GetStatusTask(
                logger=self._logger,
                serial=self._connection.serial,
                target=target)
        self._request_queue.put(t)

    def toggle_device(self, target, toggled):
        t = ToggleStatusTask(
                logger=self._logger,
                serial=self._connection.serial,
                target=target,
                toggled=toggled)
        self._request_queue.put(t)

    def raise_roller_shutter(self, target):
        t = RaiseRollerShutterTask(
                logger=self._logger,
                serial=self._connection.serial,
                target=target)
        self._request_queue.put(t)

    def lower_roller_shutter(self, target):
        t = LowerRollerShutterTask(
                logger=self._logger,
                serial=self._connection.serial,
                target=target)
        self._request_queue.put(t)

    def halt_roller_shutter(self, target):
        t = HaltRollerShutterTask(
                logger=self._logger,
                serial=self._connection.serial,
                target=target)
        self._request_queue.put(t)
