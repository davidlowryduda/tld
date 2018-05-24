
import unittest
import contextlib
from io import StringIO

from tld import *

class Basic_Task_Structure(unittest.TestCase):
    def setUp(self):
        self.td = TaskDict()
        self.td.add_task("test task 1")
        self.td.add_task("test task 2")

    def tearDown(self):
        self.td = None

    def test_add(self):
        goal = {
                 1: {'id': 1, 'text': "test task 1"},
                 2: {'id': 2, 'text': "test task 2"},
               }
        self.assertEqual(self.td.tasks, goal)

    def test_print(self):
        tmp_stdout = StringIO()
        goal = ("1 - test task 1\n"
                "2 - test task 2\n")
        with contextlib.redirect_stdout(tmp_stdout):
            self.td.print_list()
        self.assertEqual(tmp_stdout.getvalue(), goal)


if __name__ == "__main__":
    unittest.main(verbosity=2)
