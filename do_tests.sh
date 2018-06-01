#!/bin/sh
#
# A simple async testing setup.
#
# The expectation is to essentially do `echo "python tests.py" > test_commands`,
# causing that named pipe to run them. This is of course terribly insecure, but
# since when has that stopped us?
#
# I do this pathologically often from within vim using the following
# nnoremap ,t :silent exec "!echo python tests.py >> test_commands \| redraw!<CR>

if ! [ -p "test_commands" ]; then
  mkfifo test_commands
fi

while true; do
  bash -c "$(cat test_commands)";
done
