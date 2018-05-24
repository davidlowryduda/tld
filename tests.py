
import unittest
import contextlib
from io import StringIO
from optparse import OptionParser

from tld import TaskDict, build_parser

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

class Basic_Parser_Operation(unittest.TestCase):
    def test_add(self):
        input_args = ["-a", "test task 1"]
        (options, args) = build_parser().parse_args(input_args)
        self.assertTrue(options.add == True)
        self.assertTrue(args[0] == "test task 1")

    def test_list(self):
        input_args = ["-l", "othertasks"]
        (options, args) = build_parser().parse_args(input_args)
        self.assertTrue(options.name == "othertasks")


if __name__ == "__main__":
    unittest.main(verbosity=2)
