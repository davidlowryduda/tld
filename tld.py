#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A tool.
"""

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
          'creation_date': <creation_date>,
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
                    tasks = map(self._task_from_taskline, tasklines)
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
        if len(matches) == 0:
            raise KeyError("Prefix {} not in tasklist.".format(prefix))
        if len(matches) > 1:
            raise IOError("Ambiguous prefix: {}.".format(prefix))
        return self.tasks[matches[0]]

    def add_task(self, text):
        """
        Create a task with associated text.
        """
        id_ = self._hash(text)
        self.tasks[id_] = {'id': id_, 'text': text}
        return

    def delete_finished(self):
        """
        Clears the 'done' list (and file) of tasks.
        """
        self.done = {}
        return

    def edit_task(self, prefix, text):
        """
        Edit the task with given prefix to contain given text.

        Allow also perl-style `s/old/new` replacements.
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
        task['id'] = self._hash(text)
        return

    def finish_task(self, prefix):
        """
        Remove a task with associated prefix.
        """
        task = self.tasks.pop(self[prefix]['id'])
        self.done[task['id']] = task
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
                    for taskline in self._tasklines_from_tasks(tasks):
                        tfile.write(taskline)
            elif not tasks and os.path.isfile(path):
                os.remove(path)
        return

    def _tasklines_from_tasks(self, tasks):
        """
        Parse a set of tasks (e.g. taskdict.tasks.values()) into tasklines
        suitable to be written to a file.
        """
        tasklines = []
        for task in tasks:
            metapairs = [metapair for metapair in task.items()
                         if metapair[0] != 'text']
            meta_str = ", ".join("{}:{}".format(*metapair)
                                 for metapair in metapairs)
            tasklines.append('{} | {}\n'.format(task['text'], meta_str))
        return tasklines

    def print_list(self, quiet=False, grep_string=''):
        """
        Output tasklist.
        """
        kind = 'tasks'
        tasks = dict(getattr(self, kind).items())
        for id_, prefix in self._prefixes(tasks).items():
            tasks[id_]['prefix'] = prefix
        plen = max(
            map(lambda t: len(t['prefix']), tasks.values())
        ) if tasks else 0
        task_values = list(tasks.values())
        task_values.sort(key=operator.itemgetter('id'))
        for taskval in task_values:
            if grep_string.lower() not in taskval['text'].lower():
                continue
            if not quiet:
                start = '{} - '.format(taskval['prefix'].ljust(plen))
            else:
                start = ''
            print(start + taskval['text'])

    def _hash(self, text):
        """
        Return the SHA1 hash of the input string.
        """
        bytestring = text.encode(encoding='utf-8')
        return hashlib.sha1(bytestring).hexdigest()

    def _task_from_taskline(self, taskline):
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
            text, _, meta = taskline.partition('|')
            task = {'text': text.strip()}
            for piece in meta.strip().split(','):
                key, value = piece.split(':')
                task[key.strip()] = value.strip()
        else:
            text = taskline.strip()
            task = {'text': text, 'id': self._hash(text)}
        return task

    def _prefixes(self, ids):
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
                if not any(map(lambda other: other.startswith(prefix), others)):
                    prefixes[id_] = prefix
                    found = True
                    break
            if not found:
                raise KeyError("Unresolvable hash collision occurred.")
        return prefixes


def _build_parser():
    """
    Create the command line parser.

    Note: this uses optparse, which is (apparently) deprecated.
    """
    usage = "Usage: %prog [-t DIR] [-l LIST] [options] [TEXT]"
    parser = OptionParser(usage=usage)

    actions = OptionGroup(parser, "Actions",
        "If no actions are specified the TEXT will be added as a new task.")
    actions.add_option("-e", "--edit",
            dest="edit", default="",
            help="edit TASK. Can also use s/old/new",
            metavar="TASK")
    actions.add_option("-f", "--finish",
            dest="finish",
            help="mark TASK as finished",
            metavar="TASK")
    actions.add_option("-D", "--delete-finished",
            dest="delete_finished",
            action="store_true", default=False,
            help="delete finished items to save space")
    parser.add_option_group(actions)

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
    output.add_option("-q", "--quiet",
           dest="quiet",
           action="store_true", default=False,
           help="Print less detail (e.g. no task IDs)")
    output.add_option("-g", "--grep",
           dest="grep_string",
           default='',
           help="Print only tasks containing WORD. This is case insensitive",
           metavar="WORD")
    parser.add_option_group(output)
    return parser

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
    elif options.delete_finished:
        taskdict.delete_finished()
        taskdict.write(options.delete_if_empty)
    elif options.edit:
        taskdict.edit_task(options.edit, text)
        taskdict.write(options.delete_if_empty)
    elif text:
        taskdict.add_task(text)
        taskdict.write(options.delete_if_empty)
    else:
        taskdict.print_list(quiet=options.quiet,
                            grep_string=options.grep_string)

if __name__ == "__main__":
    main()
