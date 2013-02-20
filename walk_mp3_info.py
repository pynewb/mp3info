#!/usr/bin/env python
#
# Introduces:
#  Console and error output using the print function
#  String substitution using regular expressions
#  Directory traversal using walk
#  Conditional invocation of main
#

from __future__ import print_function

import argparse
import os
import os.path
import re
import sys

def print_mp3_info(path, aatpath):
    if aatpath:
        track = os.path.basename(path)
        track = re.sub('.mp3$', '', track)
        toppath = os.path.dirname(path)
        album = os.path.basename(toppath)
        toppath = os.path.dirname(toppath)
        artist = os.path.basename(toppath)
        print("Artist: {0} Album: {1} Track: {2}".format(artist, album, track))
    else:
        print(path)

def walk_mp3_info(dirpath, aatpath):
    if not os.path.isdir(dirpath):
        print(dirpath + " is not a directory", file=sys.stderr)
        return

    for root, dirs, files in os.walk(dirpath):
        for file in files:
            if (re.search('\.mp3$', file)):
                print_mp3_info(os.path.join(root, file), aatpath)

def main():
    parser = argparse.ArgumentParser(description='List MP3 file information')
    parser.add_argument('directories', metavar='directory', nargs='+',
                       help='The directories to traverse')
    parser.add_argument('--aatpath', dest='aatpath', action='store_const',
                       const=True, default=False,
                       help='Derive artist/album/track from the file path')
    
    args = parser.parse_args()
    
    for directory in args.directories:
        walk_mp3_info(os.path.expanduser(directory), args.aatpath)

if __name__ == '__main__':
    main()