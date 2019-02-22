from __future__ import print_function, division
from embarc_tools.notify import *
import unittest
import os

class TestNotify(unittest.TestCase):

    def setUp(self):
        pass

    def test_print_string(self):
        print_string("hello")
        print_string("hello", level="warning")

    def test_print_table(self):
        msg_head = ["title", "config"]
        msg_content = [["BOARD","emsk"],["BD_VER","11 22 23"]]
        msg = [msg_head, msg_content]
        print_table(msg, level=None)

    def tearDown(self):
        print("test notify")
