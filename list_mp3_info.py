#!/usr/bin/env python
#
# Introduces:
#  Argument parsing with argparse
#

import argparse
import os
import os.path
import re
import sys

def print_mp3_info(path, aatpath):
    track = os.path.basename(path)
    toppath = os.path.dirname(path)
    album = os.path.basename(toppath)
    toppath = os.path.dirname(toppath)
    artist = os.path.basename(toppath)
    
    if aatpath:
        print "Artist: {0} Album: {1} Track: {2}".format(artist, album, track)
    else:
        print path

def list_mp3_info(dirpath, aatpath):
    dirpath = os.path.expanduser(dirpath)

    if not os.path.isdir(dirpath):
        exit(dirpath + " is not a directory")

    for file in os.listdir(dirpath):
        path = os.path.join(dirpath, file)
        if (os.path.isdir(path)):
            list_mp3_info(path, aatpath)
        elif (re.search('\.mp3$', file)):
            print_mp3_info(path, aatpath)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List MP3 file information')
    parser.add_argument('directories', metavar='directory', nargs='+',
                       help='The directories to traverse')
    parser.add_argument('--aatpath', dest='aatpath', action='store_const',
                       const=True, default=False,
                       help='Derive artist/album/track from the file path')
    
    args = parser.parse_args()
    
    for directory in args.directories:
        list_mp3_info(directory, args.aatpath)