#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tld.py

tld is a tool for people who want to do things, but who might also want a bit
of organization.

tld (pronounced "told", based off of Steve Losh's t.py but with a LD twist) is
a simple command line tool that works like a (somewhat) minimal list manager.
Calling

    $ python tld.py This is a message.

will create a file called `tasks` in the current directory and put "This is a
message." (and some identifier) in that file. Calling it again will print
the contents of the file.

    $ python tld.py
    3 - This is a message.

The `3` at the start of the output is an identifier, and can be referenced.
Calling

    $ python tld.py -f 3

will mark this message as "done" and move it to a file `.tasks.done` in the
current directory.

For more options, call

    $ python tld.py -h

or visit the github page https://github.com/davidlowryduda/tld.


Tips and Tricks
---------------

For repeated use, one might use an alias like

    $ alias tld='python /path/to/tld.py --task-dir /path/to/tasks --list Tfile'

which will interact with the list `/path/to/tasks/Tfile`. Perhaps include
`--date` to always include dates in the file if you like knowing when you added
items, and display it later by calling

    $ tld --showdate


Author Info
-----------

This tool was written by David Lowry-Duda <david@lowryduda.com>. A version of
this tool can be found on github at https://github.com/davidlowryduda/tld.

This tool began as an experiment in understanding Steve Losh's implementation
of t.py (which is elegant and more pure than tld.py), but leading to something
more lasting.


License Info
------------

This is released under the MIT License.


Copyright (c) 2018 David Lowry-Duda <david@lowryduda.com>.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import datetime
import hashlib
import os
import operator
import re
from optparse import OptionParser, OptionGroup


class TaskDict():
    """
    Representation of all tasks.

    TaskDict recognizes two collections of tasks: regular and done. These are
    stored separately.

    A task is a dictionary

        {
          'id': <hash_id>,
          'text': <summary_text>,
          ... other metadata ...
        }
    """
    def __init__(self, taskdir='.', name='tasks'):
        """
        Read tasks from taskfiles if they exist.
        """
        self.tasks = {}
        self.done = {}
        self.name = name
        self.taskdir = os.path.expanduser(taskdir)
        filemap = (
            ('tasks', self.name),
            ('done', '.{}.done'.format(self.name)),
        )
        for kind, filename in filemap:
            path = os.path.join(os.path.realpath(self.taskdir), filename)
            if os.path.isdir(path):
                raise IOError("Invalid task file. File is a directory.")
            if os.path.exists(path):
                with open(path, 'r') as tfile:
                    tasklines = [taskline.strip()
                                 for taskline in tfile if taskline]
                    tasks = map(_task_from_taskline, tasklines)
                    for task in tasks:
                        getattr(self, kind)[task['id']] = task
        return

    def __getitem__(self, prefix):
        """
        Return task with given prefix.

        If more than one item found, raise an exception.
        """
        matches = list(
            filter(lambda id_: id_.startswith(prefix), self.tasks.keys())
        )
        if matches == 0:
            raise KeyError("Prefix {} not in tasklist.".format(prefix))
        if len(matches) > 1:
            raise IOError("Ambiguous prefix: {}.".format(prefix))
        return self.tasks[matches[0]]

    def add_task(self, text, tags=(), dated=False):
        """
        Create a task with associated text.
        """
        id_ = _hash(text)
        self.tasks[id_] = {'id': id_, 'text': text}
        if tags:
            self.tasks[id_]['tags'] = ','.join(tag for tag in tags)
        if dated:
            self.tasks[id_]['date'] = datetime.date.today()
        return

    def delete_finished(self):
        """
        Clears the 'done' list (and file) of tasks.
        """
        self.done = {}
        return

    def edit_task(self, prefix, text, tags=()):
        """
        Edit the task with given prefix to contain given text.

        Allow also perl-style `s/old/new` replacements on text.
        """
        task = self[prefix]
        # Allow perl-style s/old/new replacement
        if text.startswith('s/'):
            text = text[2:].strip('/')
            find, _, repl = text.partition('/')
            if not repl:
                raise IOError("perl-string {} malformed.".format('s/' + text))
            text = re.sub(find, repl, task['text'])
        task['text'] = text
        task['id'] = _hash(text)
        if tags:
            task['tags'] = ','.join(tags)
        return

    def finish_task(self, prefix):
        """
        Remove a task with associated prefix and mark it `done`.
        """
        task = self.tasks.pop(self[prefix]['id'])
        self.done[task['id']] = task
        return

    def remove_task(self, prefix):
        """
        Remove a task with associated prefix (without adding it to `done`).
        """
        self.tasks.pop(self[prefix]['id'])
        return

    def write(self, delete_if_empty=False):
        """
        Saves tasklist.
        """
        filemap = (
            ('tasks', self.name),
            ('done', '.{}.done'.format(self.name)),
        )
        for kind, filename in filemap:
            path = os.path.join(os.path.realpath(self.taskdir), filename)
            if os.path.isdir(path):
                raise IOError("Invalid task file. File is a directory.")
            tasks = sorted(getattr(self, kind).values(),
                           key=operator.itemgetter('id'))
            if tasks or not delete_if_empty:
                with open(path, 'w') as tfile:
                    for taskline in _tasklines_from_tasks(tasks):
                        tfile.write(taskline)
            elif not tasks and os.path.isfile(path):
                os.remove(path)
        return

    # pylint complains about this method having too many arguments. But as the
    # arguments are clear and have sane defaults, I simply disable the warning.
    # It would also be possible to pass in the options datastructure directly,
    # but that would lengthen the control logic in this function.
    def print_list(self,            # pylint: disable=too-many-arguments
                   kind='tasks',
                   quiet=False,
                   grep_string='',
                   showtags=False,
                   showdates=False):
        """
        Output tasklist.
        """
        tasks = dict(getattr(self, kind).items())
        set_task_prefixes(tasks)
        plen = max(
            map(lambda t: len(t['prefix']), tasks.values())
        ) if tasks else 0
        if showdates:
            dlen = max(
                map(lambda t: len(t.get('date', '')), tasks.values())
            ) if tasks else 0
        task_values = list(tasks.values())
        task_values.sort(key=operator.itemgetter('id'))
        for taskval in task_values:
            if grep_string.lower() not in taskval['text'].lower():
                continue
            if showdates:
                start = taskval.get('date', '')
                start = start.ljust(dlen)
                if dlen:
                    start += ' | '
            else:
                start = ''
            if not quiet:
                start += '{} - '.format(taskval['prefix'].ljust(plen))
            report = start + taskval['text']
            tags = taskval.get('tags', '')
            if showtags and tags:
                report += ' | tags: ' + ', '.join(tags.split(','))
            print(report)
        return


def set_task_prefixes(tasks):
    """
    Assign computed prefixes to tasks.
    """
    for id_, prefix in _prefixes(tasks).items():
        tasks[id_]['prefix'] = prefix
    return


def _build_parser():
    """
    Create the command line parser.

    Note: this uses optparse, which is (apparently) deprecated.
    """
    usage = "Usage: %prog [-t DIR] [-l LIST] [options] [TEXT]"
    parser = OptionParser(usage=usage)

    actions = OptionGroup(parser, "Actions",
                          "If no actions are specified the TEXT "
                          "will be added as a new task.")
    actions.add_option("-e", "--edit",
                       dest="edit", default="",
                       help="edit TASK. Can also use s/old/new",
                       metavar="TASK")
    actions.add_option("-f", "--finish",
                       dest="finish",
                       help="mark TASK as finished",
                       metavar="TASK")
    actions.add_option("-r", "--remove",
                       dest="remove",
                       help="remove TASK from list, without marking it 'done'.",
                       metavar="TASK")
    actions.add_option("-D", "--delete-finished",
                       dest="delete_finished",
                       action="store_true", default=False,
                       help="delete finished items to save space")
    parser.add_option_group(actions)

    entry = OptionGroup(parser, "Entry Options")
    entry.add_option("--tag",
                     dest="opttag",
                     action="append",
                     help="add TAG to tags",
                     metavar="TAG")
    entry.add_option("--date",
                     dest="dated",
                     action="store_true", default=False,
                     help="Include date in metadata")
    parser.add_option_group(entry)

    config = OptionGroup(parser, "Configuration Options")
    config.add_option("-l", "--list",
                      dest="name", default="tasks",
                      help="examine LIST",
                      metavar="LIST")
    config.add_option("-t", "--task-dir",
                      dest="taskdir", default="",
                      help="work in DIR", metavar="DIR")
    config.add_option("-d", "--delete-if-empty",
                      dest="delete_if_empty",
                      action="store_true", default=False,
                      help="delete the task file if it becomes empty")
    parser.add_option_group(config)

    output = OptionGroup(parser, "Output Options")
    output.add_option("--done",
                      dest='done',
                      action="store_true", default=False,
                      help="List done tasks instead of unfinished ones.")
    output.add_option("-q", "--quiet",
                      dest="quiet",
                      action="store_true", default=False,
                      help="Print less detail (e.g. no task IDs)")
    output.add_option("-g", "--grep",
                      dest="grep_string",
                      default='',
                      help=("Print only tasks containing WORD. "
                            "This is case insensitive"),
                      metavar="WORD")
    output.add_option("--showtags",
                      dest="showtags",
                      action="store_true", default=False,
                      help="Show tags.")
    output.add_option("--showdates",
                      dest="showdates",
                      action="store_true", default=False,
                      help="Show dates.")
    parser.add_option_group(output)
    return parser


def _hash(text):
    """
    Return the SHA1 hash of the input string.
    """
    bytestring = text.encode(encoding='utf-8')
    return hashlib.sha1(bytestring).hexdigest()


def _prefixes(ids):
    """
    Return a mapping of ids to prefixes.

    Each prefix is the shortest possible substring of the ID that
    uniquely identifies it among the given group of IDs.
    """
    prefixes = {}
    for id_ in ids:
        others = set(ids).difference([id_])
        found = False
        # iteratively test if id prefix is long enough to be unique
        for i in range(1, len(id_)+1):
            prefix = id_[:i]
            # The pf-prefix kwarg silences a pyling cell-var-from-loop warning.
            # This is safe since prefix is set on the previous line. It would
            # also work to use id_[:i] directly in loop, but I find that a bit
            # harder to read.
            if not any(map(lambda other, pf=prefix: other.startswith(pf), others)):
                prefixes[id_] = prefix
                found = True
                break
        if not found:
            raise KeyError("Unresolvable hash collision occurred.")
    return prefixes


def _tasklines_from_tasks(tasks):
    """
    Parse a set of tasks (e.g. taskdict.tasks.values()) into tasklines
    suitable to be written to a file.
    """
    tasklines = []
    for task in tasks:
        metapairs = [metapair for metapair in task.items()
                     if metapair[0] != 'text']
        meta_str = "; ".join("{}:{}".format(*metapair)
                             for metapair in metapairs)
        tasklines.append('{} | {}\n'.format(task['text'], meta_str))
    return tasklines


def _task_from_taskline(taskline):
    """
    Parse a taskline from a tasks file.

    A taskline should be in the format:

        summary text ... | meta1:meta1_value,meta2:meta2_value,...

    If the taskline has only the summary text, then the hash and metadata
    will be generated automatically upon reading. Thus it is possible to
    edit the taskfile in a plain text editor simply.

    The task returned will be a dictionary such as:

        { 'id': <hash id>,
          'text': <summary text>,
           ... other metadata ... }
    """
    if '|' in taskline:
        text, _, meta = taskline.rpartition('|')
        task = {'text': text.strip()}
        for piece in meta.strip().split(';'):
            key, value = piece.split(':')
            task[key.strip()] = value.strip()
    else:
        text = taskline.strip()
        task = {'text': text, 'id': _hash(text)}
    return task


def main(input_args=None):
    """
    Primary entry point. Parse command line and interpret taskdict.
    """
    (options, args) = _build_parser().parse_args(args=input_args)
    taskdict = TaskDict(taskdir=options.taskdir, name=options.name)
    text = ' '.join(args).strip()
    if options.finish:
        taskdict.finish_task(options.finish)
        taskdict.write(options.delete_if_empty)
    elif options.remove:
        taskdict.remove_task(options.remove)
        taskdict.write(options.delete_if_empty)
    elif options.delete_finished:
        taskdict.delete_finished()
        taskdict.write(options.delete_if_empty)
    elif options.edit:
        taskdict.edit_task(options.edit, text, tags=options.opttag)
        taskdict.write(options.delete_if_empty)
    elif text:
        taskdict.add_task(text, tags=options.opttag, dated=options.dated)
        taskdict.write(options.delete_if_empty)
    else:
        kind = 'tasks' if not options.done else 'done'
        taskdict.print_list(kind=kind,
                            quiet=options.quiet,
                            grep_string=options.grep_string,
                            showtags=options.showtags,
                            showdates=options.showdates)

if __name__ == "__main__":
    main()
