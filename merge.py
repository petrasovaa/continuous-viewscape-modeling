#!/usr/bin/env python

import glob
import re

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

def sort_nicely(l):
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key)

all = glob.glob("out_*.txt")

sort_nicely(all)

with open('all.csv', 'w') as f:
    for each in all:
        with open(each, 'r') as f1:
            line = f1.read().splitlines()[0]
            f.write(line)
            f.write('\n')

