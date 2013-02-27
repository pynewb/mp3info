#!/usr/bin/env python
#
# The ID3v2 specification is at http://id3.org
#
# Introduces:
#  class
#  self
#  docstrings
#  str.format alignment
#

from __future__ import print_function

import argparse
import os
import os.path
import re
import struct
import sys

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
        private_len, private_string = unpack_unicode(str(frame_dict['private_data']))
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

class ID3v2Printer:
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

def unpack_string(bytes):
    '''Unpacks a nul-terminated string
    
    This returns a tuple of (number-of-bytes-consumed, string)
    '''
    i = 0
    while i < len(bytes):
        if ord(bytes[i]) == 0:
            return (i + 1, bytes[0:i])
        i += 1
        
    return (len(bytes), '')

def unpack_unicode(bytes):
    '''Unpacks a nul-terminated unicode string
    
    This returns a tuple of (number-of-bytes-consumed, string)
    '''
    i = 0
    while i + 1 < len(bytes):
        uch = struct.unpack_from('<H', bytes[i:i+2])[0]
        if uch == 0:
            return (i + 2, bytes[0:i].decode('utf-16'))
        i += 2
    
    return (len(bytes), u'')

class ID3v2Parser:
    '''Parses an ID3v2 file, such as a non-ancient MP3 file
    
    A handler for this parser must have the following methods:
    
    on_path(path)
    on_aatpath(artist, album, track)
    on_raw_id3v2_header(header)
    on_id3v2_header(version, revision, flags, size)
    on_raw_id3v2dot3_frame_header(self, frame_header)
    on_id3v2dot3_frame_header(frame_type, frame_size, frame_flags)
    on_raw_id3v2dot3_frame(frame_type, frame_data)
    on_id3v2dot3_frame(frame_type, frame_data)
    '''

    def print_error(self, msg):
        print(self.path, ':', msg, file=sys.stderr)

    def parse_apic_frame(self, frame_data):
        '''Parses an ID3v2.3 attached picture frame'''
        frame_encoding = ord(frame_data[0])
        mime_len, mime_type = unpack_string(frame_data[1:])
        picture_type = ord(frame_data[1 + mime_len])
    
        if frame_encoding == 0:
            description_len, description_string = unpack_string(frame_data[2 + mime_len:])
            picture_data = frame_data[2 + mime_len + description_len:]
        elif frame_encoding == 1:
            description_len, description_string = unpack_unicode(frame_data[2 + mime_len:])
            picture_data = frame_data[2 + mime_len + description_len:]
        else:
            self.print_error("Unknown frame encoding {0:02x}".format(frame_encoding))
            return {}

        frame_dict = dict()
        frame_dict['mime_type'] = mime_type
        frame_dict['description_string'] = description_string
        frame_dict['picture_data'] = bytearray(picture_data)

        return frame_dict

    def parse_comm_frame(self, frame_data):
        '''Parses an ID3v2.3 comment frame'''
        frame_encoding, language = struct.unpack_from('b3s', frame_data)
        if language[0] == '\0':
            language = ''
        if frame_encoding == 0:
            descriptor_len, descriptor_string = unpack_string(frame_data[4:])
            comment_string = frame_data[4 + descriptor_len:]
        elif frame_encoding == 1:
            descriptor_len, descriptor_string = unpack_unicode(frame_data[4:])
            comment_string = frame_data[4 + descriptor_len:].decode('utf-16')
        else:
            self.print_error("Unknown frame encoding {0:02x}".format(frame_encoding))
            return {}

        frame_dict = dict()
        frame_dict['language'] = language
        frame_dict['descriptor_string'] = descriptor_string
        frame_dict['comment_string'] = comment_string
    
        return frame_dict

    def parse_geob_frame(self, frame_data):
        '''Parses an ID3v2.3 general encapsulated object frame'''    
        frame_encoding = ord(frame_data[0])
        mime_len, mime_type = unpack_string(frame_data[1:])
    
        if frame_encoding == 0:
            description_len, description_string = unpack_string(frame_data[1 + mime_len:])
            filename_len, filename_string = unpack_string(frame_data[1 + mime_len + description_len:])
            binary_data = frame_data[1 + mime_len + description_len + filename_len:]
        elif frame_encoding == 1:
            description_len, description_string = unpack_unicode(frame_data[1 + mime_len:])
            filename_len, filename_string = unpack_unicode(frame_data[1 + mime_len + description_len:])
            binary_data = frame_data[1 + mime_len + description_len + filename_len:]
        else:
            self.print_error("Unknown frame encoding {0:02x}".format(frame_encoding))
            return {}
    
        frame_dict = dict()
        frame_dict['mime_type'] = mime_type
        frame_dict['description_string'] = description_string
        frame_dict['filename_string'] = filename_string
        frame_dict['binary_data'] = bytearray(binary_data)

        return frame_dict

    def parse_mcdi_frame(self, frame_data):
        '''Parses an ID3v2.3 music CD identifier frame'''
        frame_dict = dict()
        frame_dict['identifier_data'] = bytearray(frame_data)
        
        return frame_dict
    
    def parse_priv_frame(self, frame_data):
        '''Parses an ID3v2.3 private frame'''
        owner_len, owner_string = unpack_string(frame_data)
        private_data = frame_data[owner_len:]
        
        frame_dict = dict()
        frame_dict['owner_string'] = owner_string
        frame_dict['private_data'] = bytearray(private_data)
        
        return frame_dict
            
    def parse_text_info_frame(self, frame_data):
        '''Parses an ID3v2.3 text info frame'''
        frame_encoding = ord(frame_data[0])
        if frame_encoding == 0:
            frame_string = frame_data[1:]
        elif frame_encoding == 1:
            frame_string = frame_data[1:].decode('utf-16')
        else:
            self.print_error("Unknown frame encoding {0:02x}".format(frame_encoding))
            return {}
        
        frame_dict = dict()
        frame_dict['frame_string'] = frame_string
        
        return frame_dict
    
    def parse_uslt_frame(self, frame_data):
        '''Parses an ID3v2.3 unsynchronized lyric translation frame'''
        frame_encoding, language = struct.unpack_from('b3s', frame_data)
        if language[0] == '\0':
            language = ''
        if frame_encoding == 0:
            descriptor_len, descriptor_string = unpack_string(frame_data[4:])
            lyrics_string = frame_data[4 + descriptor_len:]
        elif frame_encoding == 1:
            descriptor_len, descriptor_string = unpack_unicode(frame_data[4:])
            lyrics_string = frame_data[4 + descriptor_len:].decode('utf-16')
        else:
            self.print_error("Unknown frame encoding {0:02x}".format(frame_encoding))
            return {}
    
        frame_dict = dict()
        frame_dict['language'] = language
        frame_dict['descriptor_string'] = descriptor_string
        frame_dict['lyrics_string'] = lyrics_string

        return frame_dict

    def parse_id3v2dot3_frame_data(self, frame_type, frame_data):
        if frame_type == 'APIC':
            frame_dict = self.parse_apic_frame(frame_data)
        elif frame_type == 'COMM':
            frame_dict = self.parse_comm_frame(frame_data)
        elif frame_type == 'GEOB':
            frame_dict = self.parse_geob_frame(frame_data)
        elif frame_type == 'MCDI':
            frame_dict = self.parse_mcdi_frame(frame_data)
        elif frame_type == 'PRIV':
            frame_dict = self.parse_priv_frame(frame_data)
        elif frame_type == 'TALB':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TBPM':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TCOM':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TCON':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TCOP':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TENC':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TFLT':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TIT1':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TIT2':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TIT3':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TLEN':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TPE1':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TPE2':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TPE3':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TPOS':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TPUB':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TRCK':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TXXX':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'TYER':
            frame_dict = self.parse_text_info_frame(frame_data)
        elif frame_type == 'USLT':
            frame_dict = self.parse_uslt_frame(frame_data)
        else:
            self.print_error("Do not know frame type {0}".format(frame_type))
            return
        
        self.handler.on_id3v2dot3_frame(frame_type, frame_dict)

    def parse_id3v2dot3_frame(self):
    
        if self.f.tell() + 10 >= self.id3v2_size:
            return False
        
        frame_header = self.f.read(10)

        self.handler.on_raw_id3v2dot3_frame_header(frame_header)
    
        if (len(frame_header) <> 10):
            self.print_error("Frame header not 10 bytes")
            return False
    
        frame_type, frame_size, frame_flags = struct.unpack_from(">4sIH", frame_header)
    
        if frame_type == '\x00\x00\x00\x00':
            return False

        if frame_size == 0:
            return False

        self.handler.on_id3v2dot3_frame_header(frame_type, frame_size, frame_flags)    
        
        frame_data = self.f.read(frame_size)
        
        self.handler.on_raw_id3v2dot3_frame(frame_type, frame_data)

        self.parse_id3v2dot3_frame_data(frame_type, frame_data)
        
        return True

    def parse_id3v2_file(self, path, aatpath, handler):
        self.path = path
        self.handler = handler
        
        self.handler.on_path(path)
    
        if aatpath:
            track = os.path.basename(path)
            track = re.sub('.mp3$', '', track)
            toppath = os.path.dirname(path)
            album = os.path.basename(toppath)
            toppath = os.path.dirname(toppath)
            artist = os.path.basename(toppath)
            self.handler.on_aatpath(artist, album, track)
    
        with open(path, 'rb') as self.f:
            header = self.f.read(10)
    
            self.handler.on_raw_id3v2_header(header)
            
            if len(header) <> 10:
                self.print_error("No ID3v2 header")
                return
    
            file_identifier, version, revision, flags = struct.unpack_from('3sbbb', header[0:6])
            
            if file_identifier != 'ID3':
                self.print_error("No ID3v2 identifier")
                return
            
            if version == 255 or revision == 255:
                self.print_error("Invalid ID3v2 version")
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
                    self.print_error("Invalid ID3v2 size byte")
                    return
                size = (size << 7) + byte

            self.id3v2_size = size + 10

            self.handler.on_id3v2_header(version, revision, flags, size)

            if version <> 3:
                x = raw_input('Version ' + version + '...press ENTER to continue')
                return
            
            while self.parse_id3v2dot3_frame():
                pass

def walk_mp3_and_parse(dirpath, aatpath, parser_handler):
    '''Walks a directory tree for MP3 files and parses them'''
    if not os.path.isdir(dirpath):
        print(dirpath + " is not a directory", file=sys.stderr)
        return

    parser = None

    for root, dirs, files in os.walk(dirpath):
        for file in files:
            if file.endswith('.mp3'):
                if not parser:
                    parser = ID3v2Parser()
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