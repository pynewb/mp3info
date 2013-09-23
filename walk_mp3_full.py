#!/usr/bin/env python
#
# The ID3v2 specification is at http://id3.org
#
# Introduces:
#  class
#  self
#  docstrings
#  bytearray
#  str.format alignment
#
# Copyright (c) 2013, pynewb
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of pynewb nor the names of its contributors may be used to endorse or promote products derived from this software without
#     specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function

import argparse
import os
import os.path
import re
import struct
import sys

import mp3_event_parser

def isprint(ch):
    '''Gets whether a byte represents an ASCII printable character'''
    return ch >= 32 and ch < 127

def print_bytes(stringbuf):
    '''Prints bytes in hex and ASCII translation, 16 bytes per line'''
    hexbuf = ""
    buf = ""
    for c in stringbuf:
        ch = ord(c)
        hexbuf = hexbuf + "{0:02x} ".format(ch)
        if isprint(ch):
            buf = buf + c
        else:
            buf = buf + '.'
        if len(buf) >= 16:    
            print(hexbuf, ' ', buf)
            hexbuf = ""
            buf = ""
            
    if len(buf) > 0:
        while len(buf) < 16:
            hexbuf = hexbuf + '   '
            buf = buf + ' '
        print(hexbuf, ' ', buf)

def print_apic_frame(frame_dict):
    '''Prints data for an ID3v2.3 attached picture frame'''
    print("{0:>40s} : {1}".format('Attached picture mime type', frame_dict['mime_type']))
    print("{0:>40s} : {1}".format('Attached picture description', frame_dict['description_string']))
    print("{0:>40s} : {1:d}".format('Attached picture data length', len(frame_dict['picture_data'])))

def print_comm_frame(frame_dict):
    '''Prints data for an ID3v2.3 comment frame'''
    print("{0:>40s} : {1}".format('Comment language', frame_dict['language']))
    print("{0:>40s} : {1}".format('Comment description', frame_dict['descriptor_string']))
    print("{0:>40s} : {1}".format('Comment text', frame_dict['comment_string']))

def print_geob_frame(frame_dict):
    '''Prints data for an ID3v2.3 general encapsulated object frame'''    
    print("{0:>40s} : {1}".format('General encapsulated object mime type', frame_dict['mime_type']))
    print("{0:>40s} : {1}".format('General encapsulated object description', frame_dict['description_string']))
    print("{0:>40s} : {1}".format('General encapsulated object filename', frame_dict['filename_string']))
    print("{0:>40s} : {1:d}".format('General encapsulated object data length', len(frame_dict['binary_data'])))

def print_mcdi_frame(frame_dict):
    '''Prints data for an ID3v2.3 music CD identifier frame'''
    print("{0:>40s} : {1:d}".format('Music CD identifier data length', len(frame_dict['identifier_data'])))

def print_priv_frame(frame_dict):
    '''Prints data for an ID3v2.3 private frame'''
    print("{0:>40s} : {1}".format('Private owner', frame_dict['owner_string']))
    print("{0:>40s} : {1:d}".format('Private data length', len(frame_dict['private_data'])))
    if frame_dict['owner_string'] == 'WM/UniqueFileIdentifier' or frame_dict['owner_string'] == 'WM/Provider':
        private_len, private_string = mp3_event_parser.unpack_unicode(str(frame_dict['private_data']))
        if len(private_string) > 0:
            print("{0:>40s} : {1}".format('Private data', private_string))
        
def print_text_info_frame(frame_name, frame_dict):
    '''Prints data for an ID3v2.3 text info frame'''
    print("{0:>40s} : {1}".format(frame_name, frame_dict['frame_string']))

def print_uslt_frame(frame_dict):
    '''Prints data for an ID3v2.3 unsynchronized lyric translation frame'''
    print("{0:>40s} : {1}".format('Unsynchronized lyric translation language', frame_dict['language']))
    print("{0:>40s} : {1}".format('Unsynchronized lyric translation description', frame_dict['descriptor_string']))
    print("{0:>40s} : {1}".format('Unsynchronized lyric translation text', frame_dict['lyrics_string']))

class ID3v2Printer(object):
    '''A handler for the ID3v2 file parser that prints the parsed pieces'''

    def __init__(self, aatpath, hexdump, print_headers):
        self.aatpath = aatpath
        self.hexdump = hexdump
        self.print_headers = print_headers

    def on_aatpath(self, artist, album, track):
        if self.aatpath:
            print("Artist: {0} Album: {1} Track: {2}".format(artist, album, track))

    def on_id3v2_header(self, version, revision, flags, size):
        if self.print_headers:
            print("ID3v2 version {0:d} revision {1:d} flags {2:02x} size {3:d}".format(version, revision, flags, size))

    def on_id3v2dot3_frame(self, frame_type, frame_dict):
        if frame_type == 'APIC':
            print_apic_frame(frame_dict)
        elif frame_type == 'COMM':
            print_comm_frame(frame_dict)
        elif frame_type == 'GEOB':
            print_geob_frame(frame_dict)
        elif frame_type == 'MCDI':
            print_mcdi_frame(frame_dict)
        elif frame_type == 'PRIV':
            print_priv_frame(frame_dict)
        elif frame_type == 'TALB':
            print_text_info_frame('Album/Movie/Show Title', frame_dict)
        elif frame_type == 'TBPM':
            print_text_info_frame('BPM (beats per minute)', frame_dict)
        elif frame_type == 'TCOM':
            print_text_info_frame('Composer', frame_dict)
        elif frame_type == 'TCON':
            print_text_info_frame('Content type', frame_dict)
        elif frame_type == 'TCOP':
            print_text_info_frame('Copyright message', frame_dict)
        elif frame_type == 'TENC':
            print_text_info_frame('Encoded by', frame_dict)
        elif frame_type == 'TFLT':
            print_text_info_frame('File type', frame_dict)
        elif frame_type == 'TIT1':
            print_text_info_frame('Content group description', frame_dict)
        elif frame_type == 'TIT2':
            print_text_info_frame('Title/songname/content description', frame_dict)
        elif frame_type == 'TIT3':
            print_text_info_frame('Subtitle/Description refinement', frame_dict)
        elif frame_type == 'TLEN':
            print_text_info_frame('Length', frame_dict)
        elif frame_type == 'TPE1':
            print_text_info_frame('Lead performer(s)/Soloist(s)', frame_dict)
        elif frame_type == 'TPE2':
            print_text_info_frame('Band/orchestra/accompaniment', frame_dict)
        elif frame_type == 'TPE3':
            print_text_info_frame('Conductor/performer refinement', frame_dict)
        elif frame_type == 'TPOS':
            print_text_info_frame('Part of set', frame_dict)
        elif frame_type == 'TPUB':
            print_text_info_frame('Publisher', frame_dict)
        elif frame_type == 'TRCK':
            print_text_info_frame('Track number/Position in set', frame_dict)
        elif frame_type == 'TXXX':
            print_text_info_frame('User defined text information frame', frame_dict)
        elif frame_type == 'TYER':
            print_text_info_frame('Year', frame_dict)
        elif frame_type == 'USLT':
            print_uslt_frame(frame_dict)
        else:
            print("Do not know frame type", frame_type, file=sys.stderr)

    def on_id3v2dot3_frame_header(self, frame_type, frame_size, frame_flags):
        if self.print_headers:
            print("type: {0} size: {1:d} flags: {2:04x}".format(frame_type, frame_size, frame_flags))

    def on_path(self, path):
        print(path)

    def on_raw_id3v2_header(self, header):
        if self.hexdump:
            print_bytes(header)

    def on_raw_id3v2dot3_frame(self, frame_type, frame_data):
        if self.hexdump:
            print_bytes(frame_data)

    def on_raw_id3v2dot3_frame_header(self, frame_header):
        if self.hexdump:
            print_bytes(frame_header)

def walk_mp3_and_parse(dirpath, aatpath, parser_handler):
    '''Walks a directory tree for MP3 files and parses them'''
    if not os.path.isdir(dirpath):
        print(dirpath + " is not a directory", file=sys.stderr)
        return

    parser = None

    for root, dirs, files in os.walk(dirpath):
        for file in files:
            if file.endswith('.mp3'):
                if parser is None:
                    parser = mp3_event_parser.ID3v2Parser()
                parser.parse_id3v2_file(os.path.join(root, file), aatpath, parser_handler)

def main():
    '''Entry point if run as a standalone script'''
    parser = argparse.ArgumentParser(description='List MP3 file information')
    parser.add_argument('directories', metavar='directory', nargs='+',
                       help='The directories to traverse')
    parser.add_argument('--aatpath', dest='aatpath', action='store_const',
                       const=True, default=False,
                       help='Derive artist/album/track from the file path')
    parser.add_argument('--hexdump', dest='hexdump', action='store_const',
                       const=True, default=False,
                       help='Print a hex dump of frame information')
    parser.add_argument('--print-headers', dest='print_headers', action='store_const',
                       const=True, default=False,
                       help='Print file and frame headers')
    
    args = parser.parse_args()
    
    parser_handler = ID3v2Printer(args.aatpath, args.hexdump, args.print_headers)
    for directory in args.directories:
        walk_mp3_and_parse(os.path.expanduser(directory), args.aatpath, parser_handler)

if __name__ == '__main__':
    main()