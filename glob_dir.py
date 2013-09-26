#!/usr/bin/env python
#
# Introduces:
#  import
#  def
#  for..in
#  if..else
#  Console output using the print statement
#  Path manipulation
#  Directory listing via glob
#

import glob
import os.path

def list_dir(dirpath):
    wc_path = os.path.join(dirpath, '*')
    for path in glob.iglob(wc_path):
        if os.path.isdir(path):
            list_dir(path)
        else:
            print path

if __name__ == '__main__':
    list_dir('..')
    list_dir(os.path.abspath('..'))
