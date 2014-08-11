# TODO
This implementation is still incomplete.  Here's a partial TODO list:

* (easy) Interaction with [parser defaults][1]
* (easy) If type conversion doesn't work, check against how `argparse` handles [error messages][2]

## Conform to documented behavior

* (easy) Write a function that figures out `dest` from `args` in `add_argument`, instead of relying on the `Action` object

## Less Easy Stuff…
I haven't tried any of this yet. It's unlikely—but still possible!—that it could just work…

* (hard?) [Mutual Exclusion][3]
* (hard?) [Argument Groups][4]  (If implemented, these groups should get a `section` in the config file.)
* (hard?) [Sub Commands][5]  (Sub-commands should also get a `section` in the config file.)


  [1]: http://docs.python.org/dev/library/argparse.html#parser-defaults
  [2]: http://docs.python.org/dev/library/argparse.html#exiting-methods
  [3]: http://docs.python.org/dev/library/argparse.html#mutual-exclusion
  [4]: http://docs.python.org/dev/library/argparse.html#argument-groups
  [5]: http://docs.python.org/dev/library/argparse.html#sub-commands
