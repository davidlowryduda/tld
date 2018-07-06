#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for tld.py

To run, call

    $ python tests.py

Note that this set of tests wants to create a directory 'tests' and will make
files 'tests/task_test', 'tests/.task_test.done', 'integration_task_test', and
'.integration_task_test.done'. If any of these files already exists, these
tests will abort and print an error message.


Other Information
-----------------

This was written by David Lowry-Duda <david@lowryduda.com>. This is available
under the MIT License (https://opensource.org/licenses/MIT).

For more information, see tld.py or https://github.com/davidlowryduda/tld.
"""
import contextlib
import datetime
import unittest
import os
from io import StringIO

from tld import TaskDict, _build_parser, main

TASK1_ID = '3fa2e7254e7ce263b186a7ab33dbc492f4138f6d'
TASK2_ID = '3ea913db45595a91c19c50ce6f977444fa69e82a'
TASK3_ID = '417af60a94ee9643bada8dbd01a691af4e064155'
TASK4_ID = '84328fb5212fb9f5a743101d9508414299370217'


class BasicTaskStructure(unittest.TestCase):
    """
    A set of tests for each of the basic capabilities of a task dictionary.
    """
    def setUp(self):
        self.taskdict = TaskDict(name='task_test')
        self.taskdict.add_task("test task 1")
        self.taskdict.add_task("test task 2")

    def tearDown(self):
        self.taskdict = None

    def test_add(self):
        """
        Test basic adding of a task.
        """
        goal = {
            TASK1_ID: {'id': TASK1_ID, 'text': "test task 1"},
            TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"},
        }
        self.assertEqual(self.taskdict.tasks, goal)

    def test_finish(self):
        """
        Test finishing of tasks. The task should appear in done.
        """
        self.taskdict.finish_task('3f')
        task_goal = {TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"}}
        done_goal = {TASK1_ID: {'id': TASK1_ID, 'text': "test task 1"}}
        self.assertEqual(self.taskdict.tasks, task_goal)
        self.assertEqual(self.taskdict.done, done_goal)

    def test_remove(self):
        """
        Test removal of tasks. The task should not appear in done.
        """
        self.taskdict.remove_task('3f')
        task_goal = {TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"}}
        done_goal = {}
        self.assertEqual(self.taskdict.tasks, task_goal)
        self.assertEqual(self.taskdict.done, done_goal)

    def test_delete_finished(self):
        """
        Test deletion of finished tasks.
        """
        self.taskdict.finish_task('3f')
        self.taskdict.delete_finished()
        task_goal = {TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"}}
        done_goal = {}
        self.assertEqual(self.taskdict.tasks, task_goal)
        self.assertEqual(self.taskdict.done, done_goal)

    def test_date(self):
        """
        Test that dates are saved correctly.
        """
        self.taskdict.add_task("test task 3", dated=True)
        goal = {
            TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"},
            TASK1_ID: {'id': TASK1_ID, 'text': "test task 1"},
            TASK3_ID: {'id': TASK3_ID,
                       'text': "test task 3",
                       'date': datetime.date.today()}
        }
        self.assertEqual(self.taskdict.tasks, goal)
        return

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

    def test_tag(self):
        """
        Test that adding tags works.
        """
        self.taskdict.add_task("test task 3", tags=['This is a test', 'two'])
        goal = {
            TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"},
            TASK1_ID: {'id': TASK1_ID, 'text': "test task 1"},
            TASK3_ID: {'id': TASK3_ID,
                       'text': "test task 3",
                       'tags': "This is a test,two"}
        }
        self.assertEqual(self.taskdict.tasks, goal)
        return

    def test_edit_with_tag(self):
        """
        Test that editing a tag while editing changes the tag.
        """
        self.taskdict.add_task("test task 3", tags=['This is a test', 'two'])
        self.taskdict.edit_task("417", "test task 3", tags=["Repl tag"])
        goal = {
            TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"},
            TASK1_ID: {'id': TASK1_ID, 'text': "test task 1"},
            TASK3_ID: {'id': TASK3_ID,
                       'text': "test task 3",
                       'tags': "Repl tag"}
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
        """
        Test basic print functionality.
        """
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
        return

    def test_print_done(self):
        """
        Test the printing of the list of done tasks.
        """
        self.taskdict.add_task("test task 3")
        self.taskdict.finish_task('3f')
        goal_task = (
            "3 - test task 2\n"
            "4 - test task 3\n"
        )
        goal_done = (
            "3 - test task 1\n"
        )
        tmp_stdout_task = StringIO()
        with contextlib.redirect_stdout(tmp_stdout_task):
            self.taskdict.print_list()
        self.assertEqual(tmp_stdout_task.getvalue(), goal_task)
        tmp_stdout_done = StringIO()
        with contextlib.redirect_stdout(tmp_stdout_done):
            self.taskdict.print_list(kind='done')
        self.assertEqual(tmp_stdout_done.getvalue(), goal_done)
        return

    def test_quiet_print(self):
        """
        Test that quiet printing hides hashes.
        """
        tmp_stdout = StringIO()
        goal = (
            "test task 2\n"
            "test task 1\n"
        )
        with contextlib.redirect_stdout(tmp_stdout):
            self.taskdict.print_list(quiet=True)
        self.assertEqual(tmp_stdout.getvalue(), goal)
        return

    def test_grep_print(self):
        """
        Test that grep_string correctly filters output.
        """
        tmp_stdout = StringIO()
        goal = (
            "3e - test task 2\n"
        )
        with contextlib.redirect_stdout(tmp_stdout):
            self.taskdict.print_list(grep_string='2')
        self.assertEqual(tmp_stdout.getvalue(), goal)
        return

    def test_print_with_tags(self):
        """
        Test that tags are printed when showtags=True.
        """
        tmp_stdout = StringIO()
        self.taskdict.add_task("test task 3", tags=['This is a test', 'two'])
        goal = (
            "3e - test task 2\n"
            "3f - test task 1\n"
            "4  - test task 3 | tags: This is a test, two\n"
        )
        with contextlib.redirect_stdout(tmp_stdout):
            self.taskdict.print_list(showtags=True)
        self.assertEqual(tmp_stdout.getvalue(), goal)
        return


class IOTests(unittest.TestCase):
    """
    A set of tests centered on writing to the taskfile and reading the taskfile.
    """
    def setUp(self):
        if os.path.isfile('tests'):
            raise IOError("tests is not a directory.")
        if not os.path.exists('tests'):
            os.mkdir('tests')
        return

    def test_write_tasks_to_file(self):
        """
        Check that task dictionaries are written to the task file in the
        expected way.
        """
        taskdict = TaskDict(taskdir='tests', name='task_test')
        taskdict.add_task("test task 1")
        taskdict.add_task("test task 2")
        taskdict.add_task("test task 3")
        taskdict.finish_task('41')

        expected_line1 = f"test task 2 | id:{TASK2_ID}"
        expected_line2 = f"test task 1 | id:{TASK1_ID}"
        expected_done_line = f"test task 3 | id:{TASK3_ID}"

        taskdict.write()
        with open('tests/task_test', 'r') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0].strip(), expected_line1)
            self.assertEqual(lines[1].strip(), expected_line2)
        with open('tests/.task_test.done', 'r') as test_file:
            lines = test_file.readlines()
            self.assertEqual(lines[0].strip(), expected_done_line)
        return

    def test_delete_if_empty(self):
        """
        Check that delete_if_empty really deletes empty taskfiles.
        """
        taskdict = TaskDict(taskdir='tests', name='task_test')
        taskdict.write(True)
        self.assertFalse(os.path.exists('tests/task_test'))
        self.assertFalse(os.path.exists('tests/.task_test.done'))
        return

    def test_read_tasks_from_file(self):
        """
        Check that the tasks read from a taskfile are converted into a
        task dictionary correctly.
        """
        line1 = f"test task 2 | id:{TASK2_ID}"
        line2 = f"test task 1 | id:{TASK1_ID}"
        with open('tests/task_test', 'w') as test_file:
            test_file.write(line1 + '\n' + line2)
        taskdict = TaskDict(taskdir='tests', name='task_test')
        goal = {
            TASK1_ID: {'id': TASK1_ID, 'text': "test task 1"},
            TASK2_ID: {'id': TASK2_ID, 'text': "test task 2"},
        }
        self.assertEqual(taskdict.tasks, goal)
        return

    def test_read_plain_tasks_from_file(self):
        """
        Check that tasks manually written to taskfile, without hash, are
        interpreted and hashed upon read.
        """
        line1 = "test task 1"
        line2 = "test task 2"
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
    """
    A set of tests for the parser.

    Note: these were more helpful when setting up the program, and are less
    useful now. These tests probably won't grow.
    """
    def test_list(self):
        "Check that -l is captured"
        input_args = ["-l", "othertasks"]
        options = _build_parser().parse_args(input_args)
        self.assertTrue(options.name == "othertasks")

    def test_finish(self):
        "Check that -f is captured"
        input_args = ["-f", "3f"]
        options = _build_parser().parse_args(input_args)
        self.assertTrue(options.finish == "3f")

    def test_delete_finished(self):
        "Check that -D is captured"
        input_args = ["-D"]
        options = _build_parser().parse_args(input_args)
        self.assertTrue(options.delete_finished)


class IntegrationTests(unittest.TestCase):
    """
    A set of end-to-end tests.

    Calls are placed by simulating main() calls on the function. The status of
    the taskfile and the printed statements are checked.
    """
    def tearDown(self):
        if os.path.exists('integration_task_test'):
            os.remove('integration_task_test')
        if os.path.exists('.integration_task_test.done'):
            os.remove('.integration_task_test.done')

    def test_sample_run(self):
        """
        Perform a sample run, testing the file status and print status at each
        step.

        The tasks performed are the following:

        1. Add a task to the file
        2. Add a second task to the file
        3. Mark the second task done.
        4. Edit the first task.
        5. Add a task with a tag.
        """
        tmp_stdout = StringIO()
        print_args = ["-l", "integration_task_test"]

        # Add a task to the file
        input_args = ["-l", "integration_task_test", "test task 1"]
        main(input_args=input_args)
        with open("integration_task_test", "r") as tfile:
            lines = tfile.readlines()
            expected_line = f"test task 1 | id:{TASK1_ID}"
            self.assertTrue(lines[0].strip() == expected_line)

        self.compare_to_output(
            tmp_stdout,
            print_args,
            expected=(
                "3 - test task 1\n"
            ),
            msg="Adding first task to file failed."
        )

        # Add a second task
        input_args = ["-l", "integration_task_test", "test task 2"]
        main(input_args=input_args)
        with open("integration_task_test", "r") as tfile:
            lines = tfile.readlines()
            expected_line1 = f"test task 2 | id:{TASK2_ID}"
            expected_line2 = f"test task 1 | id:{TASK1_ID}"
            self.assertTrue(lines[0].strip() == expected_line1)
            self.assertTrue(lines[1].strip() == expected_line2)

        error_msg = "Adding second task failed."
        expected = (
            "3e - test task 2\n"
            "3f - test task 1\n"
        )
        self.compare_to_output(tmp_stdout, print_args, expected, msg=error_msg)

        # Mark second task done
        input_args = ["-l", "integration_task_test", "-f", "3e"]
        main(input_args=input_args)
        with open("integration_task_test", "r") as tfile:
            lines = tfile.readlines()
            expected_line2 = f"test task 1 | id:{TASK1_ID}"
            self.assertEqual(lines[0].strip(), expected_line2)
        with open(".integration_task_test.done", 'r') as tfiledone:
            lines = tfiledone.readlines()
            expected_line1 = f"test task 2 | id:{TASK2_ID}"
            self.assertEqual(lines[0].strip(), expected_line1)

        self.compare_to_output(
            tmp_stdout, print_args,
            expected=(
                "3 - test task 1\n"
            ),
            msg="Marking second task as done failed."
        )

        self.compare_to_output(
            tmp_stdout,
            print_args + ['--done'],
            expected=(
                "3 - test task 2\n"
            ),
            msg="Printing done list failed."
        )

        # Edit first task to fourth task
        input_args = ['-l', 'integration_task_test', '-e', '3', 'test task 4']
        main(input_args=input_args)
        with open("integration_task_test", "r") as tfile:
            lines = tfile.readlines()
            expected_line = f"test task 4 | id:{TASK4_ID}"
            self.assertEqual(lines[0].strip(), expected_line, msg="Edit failed.")

        self.compare_to_output(
            tmp_stdout,
            print_args,
            expected=(
                "8 - test task 4\n"
            ),
            msg="Editing of task failed."
        )

        # Add first task with tag
        input_args = ['-l', 'integration_task_test',
                      'test task 1', '--tag', 'testtag']
        main(input_args=input_args)
        with open("integration_task_test", "r") as tfile:
            lines = tfile.readlines()
            expected_line1 = f"test task 1 | id:{TASK1_ID}; tags:testtag"
            expected_line2 = f"test task 4 | id:{TASK4_ID}"
            self.assertEqual(lines[0].strip(), expected_line1)
            self.assertEqual(lines[1].strip(), expected_line2)

        self.compare_to_output(
            tmp_stdout,
            print_args + ['--showtags'],
            expected=(
                "3 - test task 1 | tags: testtag\n"
                "8 - test task 4\n"
            ),
            msg="Print with showtag failed."
        )

        self.compare_to_output(
            tmp_stdout,
            print_args,
            expected=(
                "3 - test task 1\n"
                "8 - test task 4\n"
            ),
            msg="Print without showtag failed."
        )
        return

    def compare_to_output(self, io_, print_args, expected, msg=''):
        """
        Run main with print args and assert that the result is what is
        expected. Note that this is full of side-effects. It advances main, and
        populates the StringIO instance.
        """
        # Empty StringIO by going to beginning and truncating the rest away
        io_.seek(0)
        io_.truncate(0)
        with contextlib.redirect_stdout(io_):
            main(input_args=print_args)
        self.assertEqual(io_.getvalue(), expected, msg)
        return


def do_tests():
    """
    Run the test suite.

    A few files are created for the test suite. If and of these files exist,
    this aborts and exits with an error.
    """
    FILENAMES = ['integration_task_test', '.integration_task_test.done',
                 'tests/task_test', 'tests/.task_test.done']
    if any(os.path.exists(filename) for filename in FILENAMES):
        raise IOError("One of the test_task files already exists. "
                      "Aborting to not overwrite.")
    unittest.main(verbosity=2)


if __name__ == "__main__":
    do_tests()
