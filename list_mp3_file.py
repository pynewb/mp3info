#!/usr/bin/env python
#
# Introduces:
#  String formatting
#  Additional path manipulation with basename, dirname
#

import os
import os.path
import re
import sys

def print_mp3_file(path):
    track = os.path.basename(path)
    toppath = os.path.dirname(path)
    album = os.path.basename(toppath)
    toppath = os.path.dirname(toppath)
    artist = os.path.basename(toppath)
    
    print path
    print "Artist: {0} Album: {1} Track: {2}".format(artist, album, track)

def list_mp3_file(dirpath):
    dirpath = os.path.expanduser(dirpath)

    if not os.path.isdir(dirpath):
        exit(dirpath + " is not a directory")

    for file in os.listdir(dirpath):
        path = os.path.join(dirpath, file)
        if (os.path.isdir(path)):
            list_mp3_file(path)
        elif (re.search('\.mp3$', file)):
            print_mp3_file(path)

if __name__ == '__main__':
    print sys.argv[0]
    
    if (len(sys.argv) > 1):
        for arg in sys.argv[1:]:
            list_mp3_file(arg)
    else:
        list_mp3_file(raw_input("Enter the top directory: "))