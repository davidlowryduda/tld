
import contextlib
import unittest
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
        task1_id = '3fa2e7254e7ce263b186a7ab33dbc492f4138f6d'
        task2_id = '3ea913db45595a91c19c50ce6f977444fa69e82a'
        goal = {
                 task1_id: {'id': task1_id, 'text': "test task 1"},
                 task2_id: {'id': task2_id, 'text': "test task 2"},
               }
        self.assertEqual(self.td.tasks, goal)

    def test_print(self):
        tmp_stdout = StringIO()
        goal = ("3f - test task 1\n"
                "3e - test task 2\n")
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
