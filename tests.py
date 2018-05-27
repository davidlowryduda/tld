
import contextlib
import unittest
import os
from io import StringIO
from optparse import OptionParser

from tld import TaskDict, build_parser, main

task1_id = '3fa2e7254e7ce263b186a7ab33dbc492f4138f6d'
task2_id = '3ea913db45595a91c19c50ce6f977444fa69e82a'
task3_id = '417af60a94ee9643bada8dbd01a691af4e064155'

class Basic_Task_Structure(unittest.TestCase):
    def setUp(self):
        self.td = TaskDict(name='task_test')
        self.td.add_task("test task 1")
        self.td.add_task("test task 2")

    def tearDown(self):
        self.td = None

    def test_add(self):
        goal = {
                 task1_id: {'id': task1_id, 'text': "test task 1"},
                 task2_id: {'id': task2_id, 'text': "test task 2"},
               }
        self.assertEqual(self.td.tasks, goal)

    def test_finish(self):
        self.td.finish_task('3f')
        task_goal = {task2_id: {'id': task2_id, 'text': "test task 2"}}
        done_goal = {task1_id: {'id': task1_id, 'text': "test task 1"}}
        self.assertEqual(self.td.tasks, task_goal)
        self.assertEqual(self.td.done, done_goal)

    def test_delete_finished(self):
        self.td.finish_task('3f')
        self.td.delete_finished()
        task_goal = {task2_id: {'id': task2_id, 'text': "test task 2"}}
        done_goal = {}
        self.assertEqual(self.td.tasks, task_goal)
        self.assertEqual(self.td.done, done_goal)

    def test_print(self):
        self.td.add_task("test task 3")
        tmp_stdout = StringIO()
        goal = (
                 "3e - test task 2\n"
                 "3f - test task 1\n"
                 "4  - test task 3\n"
               )
        with contextlib.redirect_stdout(tmp_stdout):
            self.td.print_list()
        self.assertEqual(tmp_stdout.getvalue(), goal)


class IO_tests(unittest.TestCase):
    def setUp(self):
        if os.path.isfile('tests'):
            raise IOError("tests is not a directory.")
        if not os.path.exists('tests'):
            os.mkdir('tests')
        return

    def test_write_tasks_to_file(self):
        self.td = TaskDict(taskdir='tests', name='task_test')
        self.td.add_task("test task 1")
        self.td.add_task("test task 2")
        self.td.add_task("test task 3")
        self.td.finish_task('41')

        expected_line1 = "test task 2 | id:3ea913db45595a91c19c50ce6f977444fa69e82a"
        expected_line2 = "test task 1 | id:3fa2e7254e7ce263b186a7ab33dbc492f4138f6d"
        expected_done_line = "test task 3 | id:417af60a94ee9643bada8dbd01a691af4e064155"

        self.td.write()
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
        self.td = TaskDict(taskdir='tests', name='task_test')
        goal = {
                 task1_id: {'id': task1_id, 'text': "test task 1"},
                 task2_id: {'id': task2_id, 'text': "test task 2"},
               }
        self.assertEqual(self.td.tasks, goal)

    def tearDown(self):
        if os.path.exists('tests/task_test'):
            os.remove('tests/task_test')
        if os.path.exists('tests/.task_test.done'):
            os.remove('tests/.task_test.done')
        if os.path.isdir('tests'):
            os.rmdir('tests')


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

    def test_finish(self):
        input_args = ["-f", "3f"]
        (options, args) = build_parser().parse_args(input_args)
        self.assertTrue(options.finish == "3f")

    def test_delete_finished(self):
        input_args = ["-D"]
        (options, args) = build_parser().parse_args(input_args)
        self.assertTrue(options.delete_finished == True)


class Integration_Tests(unittest.TestCase):
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

        # Mark first task done
        input_args = ["-l", "integration_task_test", "-f", "3e"]
        main(input_args=input_args)
        with open("integration_task_test", "r") as tfile:
            lines = tfile.readlines()
            expected_line2 = "test task 1 | id:3fa2e7254e7ce263b186a7ab33dbc492f4138f6d"
            self.assertTrue(lines[0].strip(), expected_line2)
        with open(".integration_task_test.done", 'r') as tfiledone:
            lines = tfiledone.readlines()
            expected_line1 = "test task 2 | id:3ea913db45595a91c19c50ce6f977444fa69e82a"
            self.assertTrue(lines[0].strip(), expected_line1)
        return


if __name__ == "__main__":
    unittest.main(verbosity=2)
