# tld.py

[![Build Status](https://travis-ci.com/davidlowryduda/tld.svg?branch=master)](https://travis-ci.com/davidlowryduda/tld)

`tld` is a tool for people who want to do things, but who might also want a
bit of flexibility.

`tld` (pronounced "told", based off of Steve Losh's [t.py][] but with a LD
twist) is a simple command line tool that works like a (somewhat) minimal list
manager.  Calling

[t.py]: https://github.com/sjl/t

```bash
$ python tld.py This is a message.
```

will create a file called `tasks` in the current directory and put "This is a
message." (and some identifier) in that file. Calling it again will print
the contents of the file.

```bash
$ python tld.py
3 - This is a message.
```

The `3` at the start of the output is an identifier, and can be referenced.
Calling

```bash
$ python tld.py -f 3
```

will mark this message as "done" and move it to a file `.tasks.done` in the
current directory.

For more options, call

```bash
$ python tld.py -h
```

or see the options description on the github page
https://github.com/davidlowryduda/tld.


## Why use tld?

Steve Losh designed t.py to do the *simplest thing that could possibly work*:
you can add, edit, remove, and finish elements from a list. It's simple, messy,
and has almost no features to distract you from getting in the way of doing
things. It's easy to say "I'll just organize my list a bit" and spend 15
minutes tagging, coloring, setting priorities, and so forth.

And if that works for you, great! Then t.py is enough.

`tld` does everything t.py does, except with a few more features (and a bit less
purity). In particular, `tld` supports simple date annotations, simple tagging,
and philosophically isn't against complete organization.

Where t.py encourages you to use different aliases to different tasklists for
different one level of organization, `tld` allows one to use tags in fewer
lists.


### It's Flexible

Do you want to edit a bunch of items at once? Open the list in a text editor,
and `tld` will handle the rest.

Do you want to view the list on a computer that doesn't have `tld` installed?
Open the list in a text editor.

Do you want to synchronize your list across multiple computers? Keep your lists
in a [Dropbox][] folder or a [github][] repository.

[Dropbox]: https://www.getdropbox.com/
[github]: htt[s://github.com/


### It Plays Nice with Version Control

`tld` follows the lead of other systems which keep lists in a plain text file.
This is a great idea.

`tld` also follows `t.py`'s use of random IDs to order the items in the list.
When list managers append new items to the end of the list and multiple users
edit a list, then merge conflicts will occur and require manual handling.

If order really matters, then this makes sense. But if order really matters,
then you shouldn't be using `tld`.

`tld` uses random IDs (actually SHA1 hashes) to order the list. Once a list has
a couple of items in it, adding more is far less likely to cause merge
conflicts.


## Installing tld

`tld` requires [Python][] 3 and a bash-like shell. It works on Linux, OS X, and
Windows ([with the linux subsystem][subsystem]).

[Python]: http://python.org/
[subsystem]: https://docs.microsoft.com/en-us/windows/wsl/install-win10

Installing and setting up `tld` will take about one minute.

First, [download][] the newest version or clone the github repository
(`git clone https://github.com/davidlowryduda/tld`).

[download]: https://github.com/davidlowryduda/tld/archive/master.zip

Next, decide where you want to keep your lists.  I put mine in `~/notes/tasks`
(I keep notes created from other note utilities in `~/notes/` too). Create that
directory (or whatever directory you plan on using).

```bash
mkdir -p ~/notes/tasks
```

Set up an alias to run `tld`.  Put something like this in your
`~/.bashrc` file:

```bash
alias tld='python3 ~/path/to/tld.py --task-dir ~/notes/tasks --list tasks'
```

Make sure you run `source ~/.bashrc` or restart your terminal window to make
the alias take effect. Now `tld` is ready to use.


## Using tld

`tld` is quick and easy to use, especially when used in combination with other
tools. Commandline usage is available through `tld -h` or `tld --help`, and is
a good reference once you grok the workflow.


### Add an Item

To add an item, use `tld [item description]`:

```bash
$ tld Tell my wife I love her.
$ tld Prove the Riemann Hypothesis.
$ tld "Read Steve Losh's .vimrc."
```


### List Your Items

Listing your items is even easier -- just use `tld`:

```bash
$ t
1 - Read Steve Losh's .vimrc.
a - Tell my wife I love her.
b - Prove the Riemann Hypothesis.
```

`tld` will list all of your unfinished items and their IDs. Do you not want to
see the IDs? Use the "quiet" option by using `tld -q` or `tld --quiet`.


### Finish an Item

After you're done with something, use `tld -f ID` to finish it:

```bash
$ tld -f b
$ tld
1 - Read Steve Losh's .vimrc.
a - Tell my wife I love her.
```

You can use `tld -r ID` to "remove" an item (which won't mark it as "finished".
Items marked "finished" can be listed. Items that are "removed" are just gone).


### Edit an Item

Sometimes you might want to change the wording of an item.  You can use
`tld -e ID [new description]` to do that:

```bash
$ tld -e 1 Clean my .vimrc.
$ tld
5 - Update my .vimrc.
a - Tell my wife I love her.
```

Yes, you can use sed-style substitution strings `s/old/repl`.

```bash
$ tld -e 5 s/Update/Clean/
$ tld
a - Tell my wife I love her.
e - Clean my .vimrc.
```

### List "Finished" Items

Have you marked lots of items as "finished" and you want to review them?
You can view these items with `tld --done`.

```bash
$ tld --done
b - Prove the Riemann Hypothesis.
```


### Annotate Items with Dates

Do you want to be able to remember when you added an item to the list? Use
`tld --date [description]` when you add the item to the list.

```bash
$ tld --date Write README.
$ tld
1 - Write Readme.
5 - Update my .vimrc.
a - Tell my wife I love her.
```

`tld` doesn't show these dates by default --- too much clutter. To see dates,
use `tld --showdates`.

```bash
$ tld --showdates
2018-06-01 | 1 - Write README.
           | 5 - Update my .vimrc
           | a - Tell my wife I love her.
```

You can use `--date` in your `tld` alias, and this information will only affect
the output when used with `--showdates`.


### Annotate Items with Tags

Use `tld --tag [TAG] [description]` when you add an item to the list to add a
tag.

```bash
$ tld --tag shopping Buy milk.
$ tld
1 - Write README.
5 - Update my .vimrc
9 - Buy milk.
a - Tell my wife I love her.
```

To see the tags, use `--showtags`.

```bash
$ tld --showtags
1 - Write README.
5 - Update my .vimrc
9 - Buy milk. | tags: shopping
a - Tell my wife I love her.
```


### Delete the List if it's Empty

Why keep an empty list around? You can have the list delete itself automatically
if empty. You can use the `--delete-if-empty` option in your alias:

```bash
alias tld='python3 ~/path/to/tld.py --task-dir ~/notes/tasks --list tasks --delete_if-empty'
```


## Tips and Tricks

`tld` might be simple, but it can do a lot of interesting things.


### Count Your Items

Counting your item is simple using the `wc` program:

```bash
$ tld | wc -l
4
```

### Tags, Grep, Awk, and Sed

If I have too many aliases, I forget them. I use tags and grep as a primary
level of organization. To remember what tags exist, just print them with
`tld --showtags` or `tld --showtags | grep tags`. Then print out the relevant
items through grep with `tld --showtags | grep shopping`.

```bash
$ tld --showtags | grep shopping
9 - Buy milk. | tags: shopping
```

To make it look pretty, you can cut out the tag by showing evertying before '|'
with something like awk.

```bash
$ tld --showtags | grep shopping | awk -F'|' '{print $1}'
9 - Buy milk. 
```

If you have too many tags and too many items, then perhaps having multiple lists
is a good idea for you. But you can list all the unique collections of tags
relatively easily with classic tools and sed.

```bash
$ tld --tag shopping Buy chocolate syrup.
$ tld --tag music Buy Phoenix album.
$ tld --showtags | grep tags | sed -e's/.*tags: //' | sort | uniq
music
shopping
```

### Multiple Lists


You can follow the `t.py` philosophy of organizing tasks into different lists by
adding additional aliases. For example

```bash
alias g='python ~/path/to/tld.py --task-dir ~/notes/tasks --list groceries'
alias m='python ~/path/to/tld.py --task-dir ~/notes/tasks --list music-to-buy'
alias w='python ~/path/to/tld.py --task-dir ~/notes/tasks --list wines-to-try'
```

### Distributed Bugtracking

Like the idea of distributed bug trackers like [BugsEverywhere][], but don't
want to use such a heavyweight system?  You can use `tld` instead.

Add another alias to your `~/.bashrc` file:

    alias b='python ~/path/to/tld.py --task-dir . --list bugs'

Now when you're in your project directory you can use `b` to manage the list of
bugs/tasks for that project.  Add the `bugs` file to version control and you're
all set.

Even people without `tld` installed can view the bug list, because it's plain
text.


## On Compatability with t.py

`tld` can read and operate on lists made with `t.py`, but `t.py` does not handle
the date and tag annotations from `tld`. If you never use those, then they're
interoperable (and you're essentially using `t.py` anyway).

In the future, additional metadata may be implemented in `tld`, which may
further widen this gap.


## Why Make tld?

I used Steve Losh's `t.py` for a long time before deciding to make a few
changes. When I read through his code, I thought it was pretty elegant. So I
thought it would be a good learning experience to rebuild it in roughly the same
order, but with a few changes in mind.

So really, this project is an exercise in programming that I did over about a
week to fit my whims and desires.

Those who find themselves here should really check out `t.py`. By adding new
features, I satisfy my whims --- but more features ruin the simple purity of the
original `t.py`.


## Bugs and Contributions

If you happen to use it and find a bug, let me know.

For more featureful list managers, you might checko out `todo.txt` and
`TaskWarrior`. They have lots of features and lots of knobs that one can tweak
and prettify.

If you want to contribute code to `tld`, that's great!  Fork the
[repo](https://github.com/davidlowryduda/tld) and send me a pull request.
But I've been doing this as a learning experience, and know that I might
experiment with contributed code too.
