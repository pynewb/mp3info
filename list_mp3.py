#!/usr/bin/env python
#
# Introduces:
#  Filename matching using regular expressions
#  Argument processing using sys.argv
#  Early termination with the exit function
#

import os
import os.path
import re
import sys

def list_mp3(dirpath):
    if not os.path.isdir(dirpath):
        exit(dirpath + " is not a directory")

    for file in os.listdir(dirpath):
        path = os.path.join(dirpath, file)
        if (os.path.isdir(path)):
            list_mp3(path)
        elif (re.search('\.mp3$', file)):
            print path

print sys.argv[0]

if (len(sys.argv) > 1):
    for arg in sys.argv[1:]:
        list_mp3(arg)
else:
    list_mp3(raw_input("Enter the top directory: "))