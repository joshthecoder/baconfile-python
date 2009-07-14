#!/usr/bin/python
# Copyright 2009 Joshua Roesslein <jroesslein at gmail.com>
# Licensed under the MIT License
# http://github.com/joshthecoder/baconfile-python

import urllib2
import os, sys
from datetime import datetime

import pycurl

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

def new_file(username, passwd, destpath, targetpath):
  curl = pycurl.Curl()
  curl.setopt(pycurl.USERPWD, '%s:%s' % (username, passwd))
  curl.setopt(pycurl.POST, 1)
  curl.setopt(pycurl.URL, _build_url(username, destpath))

  curl.setopt(curl.HTTPPOST, [
    ("file", (curl.FORM_FILE, targetpath))
  ])
  curl.perform()
  curl.close()

if __name__ == '__main__':
  '''Running in standalone'''
  if len(sys.argv) < 2:
    print 'Usage: baconfile <command>'
    print 'Commands:'
    print '    fetch  -  fetch file from baconfile.com'
    print '    ls     -  list folder contents'
    print '    recent -  list recently uploaded files'
    print ''
    exit(1)

  '''Fetch command'''
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

  '''ls command'''
  if sys.argv[1] == 'ls' or sys.argv[1] == 'recent':
    if sys.argv[1] == 'ls':
      if len(sys.argv) < 3:
        print 'Usage: baconfile ls <username> [folder]'
        print '   folder  -  folder to list (if not provided, lists root)'
        print ''
        exit(1)
      if len(sys.argv) == 4:
        folder = sys.argv[3]
      else: folder = ''
      items = fetch_folder(sys.argv[2], folder)
    else:
      items = fetch_recent_files()

    for i in items:
      if i.size is None: size = 'D'
      else: size = str(i.size)
      time = str(datetime.fromtimestamp(i.time_modified))
      print '%s  %s  %s  %s' % \
         (time, i.type.rjust(6), size.rjust(8), i.name)

    print '  %i items' % len(items)

  else:
    print 'Invalid command. Type "baconfile" for help.'
    exit(1)
