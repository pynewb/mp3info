#!/usr/bin/env python
#
# The ID3v2 specification is at http://id3.org
#
# Introduces:
#  More file I/O (seek and tell)
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

def print_bytes(stringbuf):
    hexbuf = ""
    buf = ""
    for c in stringbuf:
        ch = ord(c)
        hexbuf = hexbuf + "{0:02x} ".format(ch)
        if isprint(ch):
            buf = buf + c
        else:
            buf = buf + '.'
    print(hexbuf, ' ', buf)
        
def print_id3v2dot3_frame(f, id3_size):

    if f.tell() >= id3_size:
        return False
    
    frame_header = f.read(10)

    print_bytes(frame_header)

    if (len(frame_header) <> 10):
        print("Frame header not 10 bytes")
        return False

    frame_type, frame_size, frame_flags = struct.unpack_from(">4sIH", frame_header)

    if frame_size == 0:
        return False

    print("type: {0} size: {1:d} flags: {2:04x}".format(frame_type, frame_size, frame_flags))
    
    f.seek(frame_size, os.SEEK_CUR)

    return True

def print_mp3_frames(path, aatpath):
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

        print_bytes(header)
        
        if len(header) <> 10:
            print ("No ID3v2 header")
            return

        file_identifier, version, revision, flags = struct.unpack_from('3sbbb', header[0:6])
        
        if file_identifier != 'ID3':
            print("No ID3v2 identifier")
            return
        
        if version == 255 or revision == 255:
            print("Invalid ID3v2 version")
            return
        
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

        # Since just bytes are being unpacked, consider using ord()
        size_bytes = struct.unpack('bbbb', header[6:10])
        size = 0
        for byte in size_bytes:
            if byte > 127:
                print("Invalid ID3v2 size byte")
                return
            size = (size << 7) + byte

        print("ID3v2 version {0:d} revision {1:d} flags {2:02x} size {3:d}".format(version, revision, flags, size))
        if version <> 3:
            x = raw_input('Version ' + version + '...press ENTER to continue')
            return
        
        while print_id3v2dot3_frame(f, size + 10):
            pass

def walk_mp3_frames(dirpath, aatpath):
    if not os.path.isdir(dirpath):
        print(dirpath + " is not a directory", file=sys.stderr)
        return

    for root, dirs, files in os.walk(dirpath):
        for file in files:
            if file.endswith('.mp3'):
                print_mp3_frames(os.path.join(root, file), aatpath)

def main():
    parser = argparse.ArgumentParser(description='List MP3 file information')
    parser.add_argument('directories', metavar='directory', nargs='+',
                       help='The directories to traverse')
    parser.add_argument('--aatpath', dest='aatpath', action='store_const',
                       const=True, default=False,
                       help='Derive artist/album/track from the file path')
    
    args = parser.parse_args()
    
    for directory in args.directories:
        walk_mp3_frames(os.path.expanduser(directory), args.aatpath)

if __name__ == '__main__':
    main()