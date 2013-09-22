#!/usr/bin/env python

import argparse
import os
import re

#top = "c:\\users\\snichol\\music\\itunes\\itunes media\\music"
pattern = re.compile('.*\.(mp3)$', re.IGNORECASE)

class FileInfo:
  def __init__(self, path):
    self.path = path
    head, self.filename = os.path.split(path)
    head, self.album = os.path.split(head)
    head, self.artist = os.path.split(head)
    self.key = '{0}|{1}|{2}'.format(self.artist, self.album, self.filename)
    s = os.stat(path)
    self.size = s.st_size
    self.date = s.st_mtime

  def __str__(self):
    return 'key: {0} path: {1}'.format(self.key, self.path)

def find_in_tree(tree_top, match_pattern):
  for root, dirnames, filenames in os.walk(tree_top):
    for filename in filter(lambda name:match_pattern.match(name), filenames):
      yield FileInfo(os.path.join(root, filename))

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("source_dir", help="Source directory root for comparison")
  parser.add_argument("compare_dir", help="Directory root to which to compare")
  args = parser.parse_args()

  source_file_infos = {}
  for file_info in find_in_tree(args.source_dir, pattern):
    source_file_infos[file_info.key] = file_info

  compare_file_infos = {}
  for file_info in find_in_tree(args.compare_dir, pattern):
    compare_file_infos[file_info.key] = file_info

  for key in source_file_infos.keys():
    if compare_file_infos.has_key(key):
      source_info = source_file_infos[key]
      compare_info = compare_file_infos[key]
      if source_info.size != compare_info.size:
        print '{0} size {1} different than {2} {3}'.format(source_info.path, source_info.size, compare_info.path, compare_info.size)
    else:
      source_info = source_file_infos[key]
      print '{0} has no corresponding key {1} in compare'.format(source_info.path, key)
