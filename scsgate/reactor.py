""" This module contains the definition of the Reactor class.
This one is useful when dealing with concurrent access to the SCSGate
device """

import queue
import threading

from scsgate.tasks import MonitorTask, ExecutionError


class Reactor(threading.Thread):
    """ Allows concurrent access to the SCSGate device """

    def __init__(self, connection, handle_message, logger=None):
        """ Initialize the instance

        Arguments
        connection: a scsgate.Connection object
        handle_message: callback function to invoke whenever a new message
            is received
        logger: instance of logger
        """

        threading.Thread.__init__(self)
        self._connection = connection
        self._handle_message = handle_message
        self._terminate = False
        self._logger = logger
        self._request_queue = queue.Queue()

    def run(self):
        """ Starts the thread """

        task = None
        monitor_task = MonitorTask(
            notification_endpoint=self._handle_message)

        while True:
            if self._terminate:
                self._logger.info("scsgate.Reactor exiting")
                self._connection.close()
                break
            try:
                task = self._request_queue.get_nowait()
                self._logger.debug("scsgate.Reactor: got task {}".format(task))
            except queue.Empty:
                task = monitor_task

            try:
                task.execute(connection=self._connection)
            except ExecutionError as err:
                self._logger.error(err)

    def stop(self):
        """ Blocks the thread, performs cleanup of the associated
        connection """
        self._terminate = True

    def append_task(self, task):
        """ Adds a tasks to the list of the jobs to execute """
        self._request_queue.put(task)
