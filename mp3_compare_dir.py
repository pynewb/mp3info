#!/usr/bin/env python
#
# Copyright (c) 2013, pynewb
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, this list
#     of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice, this
#     list of conditions and the following disclaimer in the documentation and/or
#     other materials provided with the distribution.
#   * Neither the name of pynewb nor the names of its contributors may be used to endorse
#     or promote products derived from this software without
#     specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import print_function

import argparse
import os
import re
import sys

import mp3_event_parser

#top = "c:\\users\\snichol\\music\\itunes\\itunes media\\music"
pattern = re.compile('.*\.(mp3)$', re.IGNORECASE)

class FileInfo:
    '''Identifying information about an MP3 file'''
    
    def __init__(self):
        '''Initialize members to be populated'''
        self.path = None
        self.talb = ''
        self.tit2 = ''
        self.tpe1 = ''
        self.tpe2 = ''
        self.trck = ''

    def get_key(self):
        '''Get a key which should uniquely identify the file contents'''
        return '|'.join((self.tpe1, self.tpe2, self.talb, self.trck, self.tit2))
        
    def get_artist_album_track(self):
        '''Get the artist/album/track'''
        return '|'.join((self.tpe1 or self.tpe2, self.talb, self.tit2))
        
    def get_artist_album_trknum(self):
        '''Get the artist/album/trknum'''
        m = re.match('^(\d+)', self.trck)
        if m:
            trknum = m.group(1)
        else:
            trknum = self.trck
        return '|'.join((self.tpe1 or self.tpe2, self.talb, trknum, self.tit2))
        
    def __str__(self):
        '''String representation of this instance'''
        return 'key: {0} path: {1}'.format(self.get_key(), self.path)

class FileInfoBuilder(object):
    '''A handler for the ID3v2 file parser that builds a FileInfo'''

    def __init__(self):
        '''Initialize members'''
        self.error = None
        self.file_info = FileInfo()

    def get_error(self):
        return self.error

    def get_file_info(self):
        '''Get the FileInfo parsed from the file'''
        return self.file_info

    def on_error(self, msg):
        self.error = msg

    def on_id3v2dot3_frame(self, frame_type, frame_dict):
        '''Handle a parsed frame'''
        if frame_type == 'TALB':
            self.file_info.talb = frame_dict['frame_string']
        elif frame_type == 'TIT2':
            self.file_info.tit2 = frame_dict['frame_string']
        elif frame_type == 'TPE1':
            self.file_info.tpe1 = frame_dict['frame_string']
        elif frame_type == 'TPE2':
            self.file_info.tpe2 = frame_dict['frame_string']
        elif frame_type == 'TRCK':
            self.file_info.trck = frame_dict['frame_string']

    def on_path(self, path):
        '''Handle a file path'''
        self.file_info.path = path

def find_in_tree(tree_top, match_pattern):
    '''Find all files in a tree matching a pattern, returning a FileInfo for each'''
    parser = mp3_event_parser.ID3v2Parser()
    for root, dirnames, filenames in os.walk(tree_top):
        for filename in filter(lambda name:match_pattern.match(name), filenames):
            handler = FileInfoBuilder()
            parser.parse_id3v2_file(os.path.join(root, filename), False, handler)
            if not handler.get_error():
                yield handler.get_file_info()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("source_dir", help="Source directory root for comparison")
    parser.add_argument("compare_dir", help="Directory root to which to compare")
    args = parser.parse_args()

    print('Collecting data from source directory tree', file=sys.stderr)
    source_file_infos = {}
    for file_info in find_in_tree(args.source_dir, pattern):
        source_file_infos[file_info.get_key()] = file_info
        if (len(source_file_infos) % 10) == 0:
            print(len(source_file_infos), end='\r', file=sys.stderr)

    print(len(source_file_infos), file=sys.stderr)

    print('Collecting data from compare directory tree', file=sys.stderr)
    compare_file_infos = {}
    compare_file_infos_by_aan = {}
    compare_file_infos_by_aat = {}
    for file_info in find_in_tree(args.compare_dir, pattern):
        compare_file_infos[file_info.get_key()] = file_info
        artist_album_trknum = file_info.get_artist_album_trknum()
        artist_album_track = file_info.get_artist_album_track()
        if artist_album_trknum not in compare_file_infos_by_aan:
            compare_file_infos_by_aan[artist_album_trknum] = file_info
        else:
            print('Artist/album/trknum {0} for {1} already exists for {2}'.format(artist_album_trknum, file_info.path, compare_file_infos_by_aan[artist_album_trknum].path), file=sys.stderr)
        if artist_album_track not in compare_file_infos_by_aat:
            compare_file_infos_by_aat[artist_album_track] = file_info
        else:
            pass
#            print('Artist/album/track {0} for {1} already exists for {2}'.format(artist_album_track, file_info.path, compare_file_infos_by_aat[artist_album_track].path), file=sys.stderr)

        if (len(compare_file_infos) % 10) == 0:
            print(len(compare_file_infos), end='\r', file=sys.stderr)

    print(len(compare_file_infos), file=sys.stderr)

    for key in source_file_infos.keys():
        source_info = source_file_infos[key]
        artist_album_trknum = source_info.get_artist_album_trknum()
        artist_album_track = source_info.get_artist_album_track()
        if key in compare_file_infos:
            compare_info = compare_file_infos[key]
            # this is a most righteous match
#            print('{0} is the same as {1}'.format(source_info.path, compare_info.path))
        elif artist_album_trknum in compare_file_infos_by_aan:
            compare_info = compare_file_infos_by_aan[artist_album_trknum]
            # this is a righteous match
#            print('{0} is the same artist/album/trknum as {1}'.format(source_info.path, compare_info.path))
        elif artist_album_track in compare_file_infos_by_aat:
            compare_info = compare_file_infos_by_aat[artist_album_track]
            # this is a dubious match because of possible multiples
            print('{0} is the same artist/album/track as {1}'.format(source_info.path, compare_info.path))
        else:
            print('{0} has no corresponding key {1} or artist/album/track {2} in compare'.format(source_info.path, key, artist_album_track))

    print('Source keys')
    for key in sorted(map(lambda s: repr(s), source_file_infos.keys())):
        print(key)
    
    print('Compare keys')
    for key in sorted(map(lambda s: repr(s), compare_file_infos.keys())):
        print(key)
    
