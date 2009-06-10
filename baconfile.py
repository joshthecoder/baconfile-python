# Copyright 2009 Joshua Roesslein
# Licensed under the MIT License

import urllib2
import os, sys

if sys.version_info < (2,6,):
  import simplejson as json
else:
  import json

baconfile_url = 'http://baconfile.com/'

class FolderItem(object):
  def __init__(self, data):
    self.id = data['id']
    self.size = data['size']
    self.permalink = data['permalink']
    self.name = data['name']
    self.url = data['url']
    self.file_url = data['file_url']
    self.time_modified = data['time_modified']
    self.twitter_url = data['twitter_url']
    self.tiny_url = data['tiny_url']
    self.user = data['user']
    self.is_folder = data['is_folder']
    self.path = data['path']
    self.content_type = data['content_type']
    self.type = data['type']
    self.description = data['description']

  def read_file(self, amt=None):
    r = urllib2.urlopen(self.file_url)
    return r.read(amt)

  def save_file(self, filepath):
    f = open(filepath, 'wb')
    f.write(self.read_file())
    f.close()

def _build_url(username, path):
  return baconfile_url + os.path.join(username, path) + '.json'

def fetch_folder(username, folder):
  r = urllib2.urlopen(_build_url(username, folder))
  items = json.loads(r.read())['items']
  return list(FolderItem(i) for i in items) 

def fetch_file(username, filepath):
  r = urllib2.urlopen(_build_url(username, filepath))
  item = json.loads(r.read())
  return FolderItem(item)

def fetch_recent_files():
  r = urllib2.urlopen(baconfile_url + 'public.json')
  items = json.loads(r.read())['items']
  return list(FolderItem(i) for i in items)

if __name__ == '__main__':
  '''Running in standalone'''
  if len(sys.argv) < 2:
    print 'Usage: baconfile <command>'
    print 'Commands:'
    print '    fetch  -  fetch file from baconfile.com'
    print '    ls     -  list folder contents'
    print ''
    exit(1)

  if sys.argv[1] == 'fetch':
    if len(sys.argv) < 4:
      print 'Usage: baconfile fetch <username> <remotefile> [dest]'
      print '   remotefile  -  path on baconfile.com where file is stored'
      print '   dest        -  local path to save file (optional)'
      print 'example: baconfile fetch someuser stuff/file.txt'
      print ''
      exit(1)
    if len(sys.argv) == 5:
      dest = sys.argv[4]
    else: dest = sys.argv[3].rsplit('/',1)[-1]

    try:
      f = fetch_file(sys.argv[2], sys.argv[3])
      f.save_file(dest)
    except urllib2.HTTPError, e:
      print 'Unable to fetch file: %s' % e
      exit(1)

  else:
    print 'Invalid command. Type "baconfile" for help.'
    exit(1)
