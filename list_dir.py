#!/usr/bin/env python
#
# Introduces:
#  Console input using the raw_input function
#  Directory listing using listdir
#

import os
import os.path

def list_dir(dirpath):
    for file in os.listdir(dirpath):
        path = os.path.join(dirpath, file)
        if os.path.isdir(path):
            list_dir(path)
        else:
            print path

if __name__ == '__main__':
    dir = raw_input("Enter the top directory: ")
    list_dir(os.path.expanduser(dir))