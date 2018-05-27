#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
        filemap = (
                    ('tasks', self.name),
                    ('done', '.{}.done'.format(self.name)),
                  )
        for kind, filename in filemap:
            if os.path.isdir(filename):
                raise IOError("Invalid task file. File is a directory.")
            with open(filename, 'w') as tfile:
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
#        tasks.sort(key=operator.itemgetter('id'))
        for id_, prefix in self._prefixes(tasks).items():
            start = '{} -'.format(prefix)
            print(start + ' ' + tasks[id_]['text'])

    def _hash(self, text):
        """
        Return the SHA1 hash of the input string.
        """
        bytestring = text.encode(encoding='utf-8')
        return hashlib.sha1(bytestring).hexdigest()

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
        td.write()
    else:
        td.print_list()
