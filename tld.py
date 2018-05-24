#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import operator
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
    def __init__(self, name='tasks'):
        """
        Read tasks from taskfiles if they exist.
        """
        self.tasks = {}
        self.done = {}
        self.name = name
        self.counter = 0

    def add_task(self, text):
        """
        Create a task with associated text.
        """
        id_ = self._hash(text)
        self.tasks[id_] = {'id': id_, 'text': text}

    def write(self):
        """
        Saves tasklist.
        """
        pass

    def print_list(self):
        """
        Output tasklist.
        """
        kind = 'tasks'
        tasks = dict(getattr(self, kind).items())
#        tasks.sort(key=operator.itemgetter('id'))
        for t in tasks.values():
            start = '{} -'.format(t['id'])
            print(start + ' ' + t['text'])

    def _hash(self, text):
        self.counter += 1
        return self.counter


def build_parser():
    parser = OptionParser()
    parser.add_option("-a",
                      action="store_true",
                      dest="add",
                      default=False,
                      help="add text to task (default)")
    parser.add_option("-l",
                      dest="name",
                      default="tasks",
                      help="examine LIST",
                      metavar="LIST")
    return parser

if __name__ == "__main__":
    td = TaskDict()
    (options, args) = build_parser().parse_args()
    text = ' '.join(args)
    if text:
        td.add_task(text)
#        td.write()
    else:
        td.print_list()
