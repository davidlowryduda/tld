#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A tool.
"""

import os
import operator
import hashlib
from optparse import OptionParser


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
                                 for taskline in tfile.readlines() if taskline]
                    tasks = map(self._task_from_taskline, tasklines)
                    for task in tasks:
                        getattr(self, kind)[task['id']] = task
        return

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

    def finish_task(self, prefix):
        """
        Remove a task with associated prefix.
        """
        matches = list(
            filter(lambda id_: id_.startswith(prefix), self.tasks.keys())
        )
        if len(matches) > 1:
            raise IOError("Ambiguous prefix. Unable to continue.")
        task = self.tasks.pop(matches[0])
        self.done[task['id']] = task
        return

    def write(self):
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
            with open(path, 'w') as tfile:
                tasks = list(getattr(self, kind).values())
                tasks.sort(key=operator.itemgetter('id'))
                for task in tasks:
                    metapairs = [metapair for metapair in task.items()
                                 if metapair[0] != 'text']
                    meta_str = ", ".join("{}:{}".format(*metapair)
                                         for metapair in metapairs)
                    tfile.write('%s | %s\n' % (task['text'], meta_str))

    def print_list(self):
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
            start = '{} -'.format(taskval['prefix'].ljust(plen))
            print(start + ' ' + taskval['text'])

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

        The task returned will be a dictionary such as:

            { 'id': <hash id>,
              'text': <summary text>,
               ... other metadata ... }
        """
        text, _, meta = taskline.partition('|')
        task = {'text': text.strip()}
        for piece in meta.strip().split(','):
            key, value = piece.split(':')
            task[key.strip()] = value.strip()
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
            # iteratively test if id prefix is long enough to be unique
            for i in range(1, len(id_)+1):
                prefix = id_[:i]
                if not any(map(lambda other: other.startswith(prefix), others)):
                    prefixes[id_] = prefix
                    break
        return prefixes


def build_parser():
    """
    Create the command line parser.

    Note: this uses optparse, which is (apparently) deprecated.
    """
    parser = OptionParser()

    parser.add_option("-a", "--add",
                      dest="add",
                      action="store_true", default=False,
                      help="add text to task (default)")

    parser.add_option("-l", "--list",
                      dest="name", default="tasks",
                      help="examine LIST",
                      metavar="LIST")

    parser.add_option("-f", "--finish",
                      dest="finish",
                      help="mark TASK as finished",
                      metavar="TASK")

    parser.add_option("-D", "--delete-finished",
                      dest="delete_finished",
                      action="store_true", default=False,
                      help="delete finished items to save space")

    parser.add_option("-t", "--task-dir",
                      dest="taskdir", default="",
                      help="work in DIR", metavar="DIR")
    return parser

def main(input_args=None):
    """
    Primary entry point. Parse command line and interpret taskdict.
    """
    (options, args) = build_parser().parse_args(args=input_args)
    taskdict = TaskDict(taskdir=options.taskdir, name=options.name)
    text = ' '.join(args)
    if options.finish:
        taskdict.finish_task(options.finish)
        taskdict.write()
    elif options.delete_finished:
        taskdict.delete_finished()
        taskdict.write()
    elif text:
        taskdict.add_task(text)
        taskdict.write()
    else:
        taskdict.print_list()

if __name__ == "__main__":
    main()
