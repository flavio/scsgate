import unittest
import os
import sys

# inject local copy to avoid testing the installed version instead of the
# development one
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scsgate import messages

class TestMessages(unittest.TestCase):
    """ Test Message classses """

    def test_parse_ack(self):
        data = b"A5"
        msg = messages.parse(data)
        self.assertIsInstance(msg, messages.AckMessage)
        self.assertIsNone(msg.entity)

    def test_parse_unknown_long_message(self):
        data = b"A8330015000026A3"
        msg = messages.parse(data)
        self.assertIsInstance(msg, messages.UnknownMessage)
        self.assertEqual(msg.data, data.decode("ascii"))
        self.assertIsNone(msg.entity)

    def test_parse_turn_on_command(self):
        data = b"A83300120021A3"
        msg = messages.parse(data)
        self.assertIsInstance(msg, messages.CommandMessage)
        self.assertEqual(msg.data, data.decode("ascii"))
        self.assertEqual(msg.status, "on")
        self.assertEqual(msg.destination, "33")
        self.assertEqual(msg.source, "00")
        self.assertEqual(msg.destination, msg.entity)

    def test_parse_turn_off_command(self):
        data = b"A83300120121A3"
        msg = messages.parse(data)
        self.assertIsInstance(msg, messages.CommandMessage)
        self.assertEqual(msg.data, data.decode("ascii"))
        self.assertEqual(msg.status, "off")
        self.assertEqual(msg.destination, "33")
        self.assertEqual(msg.source, "00")

    def test_parse_turn_on_state(self):
        data = b"A8B833120098A3"
        msg = messages.parse(data)
        self.assertIsInstance(msg, messages.StateMessage)
        self.assertEqual(msg.data, data.decode("ascii"))
        self.assertEqual(msg.status, "on")
        self.assertEqual(msg.source, "33")

    def test_parse_turn_off_state(self):
        data = b"A8B833120198A3"
        msg = messages.parse(data)
        self.assertIsInstance(msg, messages.StateMessage)
        self.assertEqual(msg.data, data.decode("ascii"))
        self.assertEqual(msg.status, "off")
        self.assertEqual(msg.source, "33")

    def test_parse_request_status(self):
        data = b"A83300150026A3"
        msg = messages.parse(data)
        self.assertIsInstance(msg, messages.RequestStatusMessage)
        self.assertEqual(msg.data, data.decode("ascii"))
        self.assertEqual(msg.destination, "33")
        self.assertEqual(msg.source, "00")

    def test_compute_checksum_bytes(self):
        test_data = [
            {
                'bytes': [b"14", b"00", b"12", b"01"],
                'check': b"07"
            },
            {
                'bytes': [b"14", b"00", b"12", b"00"],
                'check': b"06"
            },
            {
                'bytes': [b"33", b"00", b"12", b"00"],
                'check': b"21"
            },
            {
                'bytes': [b"B8", b"33", b"12", b"01"],
                'check': b"98"
            },
            {
                'bytes': [b"33", b"00", b"15", b"00"],
                'check': b"26"
            },
            {
                'bytes': [b"b8", b"33", b"12", b"00"],
                'check': b"99"
            },
            {
                'bytes': [b"36", b"00", b"12", b"01"],
                'check': b"25"
            },
            {
                'bytes': [b"96", b"BE", b"31", b"00"],
                'check': b"19"
            }
        ]

        for d in test_data:
            bytes = d['bytes']
            expected = d['check']
            actual = messages.checksum_bytes(bytes)
            self.assertEqual(
                actual,
                expected,
                "Expected {0} to return {1} instead got {2}".format(
                    bytes,
                    expected,
                    actual)
            )
