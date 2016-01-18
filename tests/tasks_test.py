import unittest
from unittest.mock import MagicMock
import os
import sys

# inject local copy to avoid testing the installed version instead of the
# development one
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scsgate.tasks import *

class TestTasks(unittest.TestCase):
    """ Test Task classses """

    def setUp(self):
        self.serial = MagicMock()

    def test_get_status_telegram(self):
        task = GetStatusTask(
                serial=self.serial,
                target="12")
        self.assertEqual(
            b'A81200150007A3',
            task.telegram())
