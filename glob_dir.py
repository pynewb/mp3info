#!/usr/bin/env python
#
# Introduces:
#  Console output using the print statement
#  Path manipulation
#  Directory listing via glo
#

import glob
import os.path

def list_dir(dirpath):
    wc_path = os.path.join(dirpath, '*')
    for path in glob.iglob(wc_path):
        if (os.path.isdir(path)):
            list_dir(path)
        else:
            print path

list_dir('..')
list_dir(os.path.abspath('..'))
