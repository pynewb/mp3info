#!/usr/bin/env python
#
# The IDv2 specification is at http://id3.org
#
# Introduces:
#  with
#  File I/O
#  Unpacking binary data with struct
#  Using str.endswith instead of a regular expression
#

from __future__ import print_function

import argparse
import os
import os.path
import re
import struct
import sys

def isprint(ch):
    return ch >= 32 and ch < 127

def print_mp3_header(path, aatpath):
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

    with open(path, 'rb') as f:
        header = f.read(10)

        hexbuf = ""
        buf = ""
        for c in header:
            ch = ord(c)
            hexbuf = hexbuf + "{0:02x} ".format(ch)
            if isprint(ch):
                buf = buf + c
            else:
                buf = buf + '.'
        print(hexbuf, ' ', buf)
        
        if len(header) <> 10:
            print ("No ID3v2 header")
            return

        if header[0:3] != 'ID3':
            print("No ID3v2 indicator")
            return
        
        version, revision = struct.unpack('<bb', header[3:5])
        if version == 255 or revision == 255:
            print("Invalid ID3v2 version")
            return
        
        flags = ord(header[5])
        unsynchronization = False
        compressed = False
        extended_header = False
        experimental = False
        if version == 2:
            unsynchronization = (flags & 0x80) != 0
            compressed = (flags & 0x40) != 0
        elif version == 3:
            unsynchronization = (flags & 0x80) != 0
            extended_header = (flags & 0x40) != 0
            experimental = (flags & 0x20) != 0

        size_bytes = struct.unpack('<bbbb', header[6:10])
        size = 0
        for byte in size_bytes:
            if byte > 127:
                print("Invalid ID3v2 size byte")
                return
            size = (size << 7) + byte

        print("ID3 version {0:d} revision {1:d} flags {2:02x} size {3:d}".format(version, revision, flags, size))
        if version <> 3:
            x = raw_input('Version ' + version + '...press ENTER to continue')

def walk_mp3_header(dirpath, aatpath):
    if not os.path.isdir(dirpath):
        print(dirpath + " is not a directory", file=sys.stderr)
        return

    for root, dirs, files in os.walk(dirpath):
        for file in files:
            if file.endswith('.mp3'):
                print_mp3_header(os.path.join(root, file), aatpath)

def main():
    parser = argparse.ArgumentParser(description='List MP3 file information')
    parser.add_argument('directories', metavar='directory', nargs='+',
                       help='The directories to traverse')
    parser.add_argument('--aatpath', dest='aatpath', action='store_const',
                       const=True, default=False,
                       help='Derive artist/album/track from the file path')
    
    args = parser.parse_args()
    
    for directory in args.directories:
        walk_mp3_header(os.path.expanduser(directory), args.aatpath)

if __name__ == '__main__':
    main()