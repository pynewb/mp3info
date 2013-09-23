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

import struct
import sys

class ID3v2Parser(object):
    '''Parses an ID3v2 file, such as a non-ancient MP3 file
    
    This is an event-based parser, a la SAX, that parses the
    file and invokes user callbacks for particular file parts
    
    A handler for this parser must have the following methods:
    
    on_path(path)
    on_aatpath(artist, album, track)
    on_raw_id3v2_header(header)
    on_id3v2_header(version, revision, flags, size)
    on_raw_id3v2dot3_frame_header(self, frame_header)
    on_id3v2dot3_frame_header(frame_type, frame_size, frame_flags)
    on_raw_id3v2dot3_frame(frame_type, frame_data)
    on_id3v2dot3_frame(frame_type, frame_data)

    The ID3v2 specification is at http://id3.org
    
    TODO: support handlers that only implement a subset of these methods
    '''

    def __print_error(self, msg):
        '''Print an error to stderr (TODO: pass to error handling method)'''
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
            self.__print_error("Unknown frame encoding {0:02x}".format(frame_encoding))
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
            self.__print_error("Unknown frame encoding {0:02x}".format(frame_encoding))
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
            self.__print_error("Unknown frame encoding {0:02x}".format(frame_encoding))
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
            self.__print_error("Unknown frame encoding {0:02x}".format(frame_encoding))
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
            self.__print_error("Unknown frame encoding {0:02x}".format(frame_encoding))
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
            self.__print_error("Do not know frame type {0}".format(frame_type))
            return
        
        self.handler.on_id3v2dot3_frame(frame_type, frame_dict)

    def parse_id3v2dot3_frame(self):
    
        if self.f.tell() + 10 >= self.id3v2_size:
            return False
        
        frame_header = self.f.read(10)

        self.handler.on_raw_id3v2dot3_frame_header(frame_header)
    
        if (len(frame_header) <> 10):
            self.__print_error("Frame header not 10 bytes")
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
                self.__print_error("No ID3v2 header")
                return
    
            file_identifier, version, revision, flags = struct.unpack_from('3sbbb', header[0:6])
            
            if file_identifier != 'ID3':
                self.__print_error("No ID3v2 identifier")
                return
            
            if version == 255 or revision == 255:
                self.__print_error("Invalid ID3v2 version")
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
                    self.__print_error("Invalid ID3v2 size byte")
                    return
                size = (size << 7) + byte

            self.id3v2_size = size + 10

            self.handler.on_id3v2_header(version, revision, flags, size)

            if version <> 3:
                self.print_error("Version {0} is not 3".format(version))
                return
            
            while self.parse_id3v2dot3_frame():
                pass

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
