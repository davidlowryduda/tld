"""
Test suite.
"""
import contextlib
import unittest
import os
from io import StringIO
from optparse import OptionParser

from tld import TaskDict, _build_parser, main

TASK1_ID = '3fa2e7254e7ce263b186a7ab33dbc492f4138f6d'
TASK2_ID = '3ea913db45595a91c19c50ce6f977444fa69e82a'
TASK3_ID = '417af60a94ee9643bada8dbd01a691af4e064155'
TASK4_ID = '84328fb5212fb9f5a743101d9508414299370217'

class BasicTaskStructure(unittest.TestCase):
    def setUp(self):
        self.taskdict = TaskDict(name='task_test')
        self.taskdict.add_task("test task 1")
        self.taskdict.add_task("test task 2")

    def tearDown(self):
        self.taskdict = None

    def test_add(self):
        goal = {
            TASK1_ID: {'id': TASK1_ID, 'text': "test task 1"},
            TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"},
        }
        self.assertEqual(self.taskdict.tasks, goal)

    def test_finish(self):
        self.taskdict.finish_task('3f')
        task_goal = {TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"}}
        done_goal = {TASK1_ID: {'id': TASK1_ID, 'text': "test task 1"}}
        self.assertEqual(self.taskdict.tasks, task_goal)
        self.assertEqual(self.taskdict.done, done_goal)

    def test_delete_finished(self):
        self.taskdict.finish_task('3f')
        self.taskdict.delete_finished()
        task_goal = {TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"}}
        done_goal = {}
        self.assertEqual(self.taskdict.tasks, task_goal)
        self.assertEqual(self.taskdict.done, done_goal)

    def test_edit(self):
        """
        Test that one can edit tasks.

        Note that the original ID as a key doesn't change, even though the
        embedded subID does. This is corrected on next read.
        """
        self.taskdict.edit_task('3f', "test task 3")
        goal = {
            TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"},
            TASK1_ID: {'id': TASK3_ID, 'text': "test task 3"},
        }
        self.assertEqual(self.taskdict.tasks, goal)
        return

    def test_sub_replace_edit(self):
        """
        Test that one can edit tasks through `s/old/new` notation.

        Note that the original ID as a key doesn't change, even through the
        embedded subID does. This is corrected on next read.
        """
        self.taskdict.edit_task('3f', "s/1/3")
        goal = {
            TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"},
            TASK1_ID: {'id': TASK3_ID, 'text': "test task 3"},
        }
        self.assertEqual(self.taskdict.tasks, goal)
        return

    def test_print(self):
        self.taskdict.add_task("test task 3")
        tmp_stdout = StringIO()
        goal = (
            "3e - test task 2\n"
            "3f - test task 1\n"
            "4  - test task 3\n"
        )
        with contextlib.redirect_stdout(tmp_stdout):
            self.taskdict.print_list()
        self.assertEqual(tmp_stdout.getvalue(), goal)


class IOTests(unittest.TestCase):
    def setUp(self):
        if os.path.isfile('tests'):
            raise IOError("tests is not a directory.")
        if not os.path.exists('tests'):
            os.mkdir('tests')
        return

    def test_write_tasks_to_file(self):
        taskdict = TaskDict(taskdir='tests', name='task_test')
        taskdict.add_task("test task 1")
        taskdict.add_task("test task 2")
        taskdict.add_task("test task 3")
        taskdict.finish_task('41')

        expected_line1 = "test task 2 | id:3ea913db45595a91c19c50ce6f977444fa69e82a"
        expected_line2 = "test task 1 | id:3fa2e7254e7ce263b186a7ab33dbc492f4138f6d"
        expected_done_line = "test task 3 | id:417af60a94ee9643bada8dbd01a691af4e064155"

        taskdict.write()
        with open('tests/task_test', 'r') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0].strip(), expected_line1)
            self.assertEqual(lines[1].strip(), expected_line2)
        with open('tests/.task_test.done', 'r') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0].strip(), expected_done_line)

    def test_read_tasks_from_file(self):
        line1 = "test task 2 | id:3ea913db45595a91c19c50ce6f977444fa69e82a"
        line2 = "test task 1 | id:3fa2e7254e7ce263b186a7ab33dbc492f4138f6d"
        with open('tests/task_test', 'w') as test_file:
            test_file.write(line1 + '\n' + line2)
        taskdict = TaskDict(taskdir='tests', name='task_test')
        goal = {
            TASK1_ID: {'id': TASK1_ID, 'text': "test task 1"},
            TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"},
        }
        self.assertEqual(taskdict.tasks, goal)

    def tearDown(self):
        if os.path.exists('tests/task_test'):
            os.remove('tests/task_test')
        if os.path.exists('tests/.task_test.done'):
            os.remove('tests/.task_test.done')
        if os.path.isdir('tests'):
            os.rmdir('tests')


class BasicParserOperation(unittest.TestCase):
    def test_add(self):
        input_args = ["-a", "test task 1"]
        (options, args) = _build_parser().parse_args(input_args)
        self.assertTrue(options.add)
        self.assertTrue(args[0] == "test task 1")

    def test_list(self):
        input_args = ["-l", "othertasks"]
        (options, _) = _build_parser().parse_args(input_args)
        self.assertTrue(options.name == "othertasks")

    def test_finish(self):
        input_args = ["-f", "3f"]
        (options, _) = _build_parser().parse_args(input_args)
        self.assertTrue(options.finish == "3f")

    def test_delete_finished(self):
        input_args = ["-D"]
        (options, _) = _build_parser().parse_args(input_args)
        self.assertTrue(options.delete_finished)


class IntegrationTests(unittest.TestCase):
    def tearDown(self):
        if os.path.exists('integration_task_test'):
            os.remove('integration_task_test')
        if os.path.exists('.integration_task_test.done'):
            os.remove('.integration_task_test.done')

    def test_sample_run(self):
        # Add a task to the file
        input_args = ["-l", "integration_task_test", "-a", "test task 1"]
        main(input_args=input_args)
        with open("integration_task_test", "r") as tfile:
            lines = tfile.readlines()
            expected_line = "test task 1 | id:3fa2e7254e7ce263b186a7ab33dbc492f4138f6d"
            self.assertTrue(lines[0].strip(), expected_line)

        # Add a second task
        input_args = ["-l", "integration_task_test", "-a", "test task 2"]
        main(input_args=input_args)
        with open("integration_task_test", "r") as tfile:
            lines = tfile.readlines()
            expected_line1 = "test task 2 | id:3ea913db45595a91c19c50ce6f977444fa69e82a"
            expected_line2 = "test task 1 | id:3fa2e7254e7ce263b186a7ab33dbc492f4138f6d"
            self.assertTrue(lines[0].strip(), expected_line1)
            self.assertTrue(lines[1].strip(), expected_line2)

        # Mark second task done
        input_args = ["-l", "integration_task_test", "-f", "3e"]
        main(input_args=input_args)
        with open("integration_task_test", "r") as tfile:
            lines = tfile.readlines()
            expected_line2 = "test task 1 | id:3fa2e7254e7ce263b186a7ab33dbc492f4138f6d"
            self.assertEqual(lines[0].strip(), expected_line2)
        with open(".integration_task_test.done", 'r') as tfiledone:
            lines = tfiledone.readlines()
            expected_line1 = "test task 2 | id:3ea913db45595a91c19c50ce6f977444fa69e82a"
            self.assertEqual(lines[0].strip(), expected_line1)

        # Edit first task to fourth task
        input_args = ['-l', 'integration_task_test', '-e', '3', 'test task 4']
        main(input_args=input_args)
        with open("integration_task_test", "r") as tfile:
            lines = tfile.readlines()
            expected_line = "test task 4 | id:84328fb5212fb9f5a743101d9508414299370217"
            self.assertEqual(lines[0].strip(), expected_line, msg="Edit failed.")
        return


if __name__ == "__main__":
    unittest.main(verbosity=2)
