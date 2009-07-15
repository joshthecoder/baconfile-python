#!/usr/bin/python
# Copyright 2009 Joshua Roesslein <jroesslein at gmail.com>
# Licensed under the MIT License
# http://github.com/joshthecoder/baconfile-python

import urllib
import urllib2
import base64
import os, sys
from datetime import datetime
from getpass import getpass

if sys.version_info < (2,6,):
  import simplejson as json
else:
  import json

baconfile_url = 'http://baconfile.com/'

"""Baconfile library"""

class FolderItem(object):
  def __init__(self, data):
    self.id = data.get('id')
    self.size = data.get('size', 0)
    self.permalink = data.get('permalink')
    self.name = data.get('name')
    self.url = data.get('url')
    self.file_url = data.get('file_url')
    self.time_modified = data.get('time_modified')
    self.tiny_url = data.get('tiny_url')
    self.user = data.get('user')
    self.is_folder = data.get('is_folder')
    self.path = data.get('path')
    self.content_type = data.get('content_type')
    self.type = data.get('type')
    self.description = data.get('description')

  def read_file(self, amt=None):
    r = urllib2.urlopen(self.file_url)
    return r.read(amt)

  def save_file(self, filepath):
    f = open(filepath, 'wb')
    f.write(self.read_file())
    f.close()

class BaconfileError(Exception):
  def __init__(self, reason='Baconfile error occured.'):
    self.reason = reason
  def __str__(self):
    return self.reason

def _build_url(username, path):
  return baconfile_url + os.path.join(username, path) + '.json'

def _make_request(url, data=None, headers={}):
  try:
    headers['User-Agent'] = 'baconfilepy/1.0'
    req = urllib2.Request(url, data, headers)
    return urllib2.urlopen(req)
  except urllib2.HTTPError, e:
    try:
      reason = str(json.loads(e.read())['error']['message'])
    except Exception:
      reason = 'unkown'
    raise BaconfileError(reason)

def fetch_folder(username, folder):
  r = _make_request(_build_url(username, folder))
  items = json.loads(r.read())['items']
  return list(FolderItem(i) for i in items) 

def fetch_file(username, filepath):
  r = _make_request(_build_url(username, filepath))
  item = json.loads(r.read())
  return FolderItem(item)

def fetch_recent_files():
  r = _make_request(baconfile_url + 'public.json')
  items = json.loads(r.read())['items']
  return list(FolderItem(i) for i in items)

def _build_headers(credentials):
  return {
    'Authorization':
      'Basic %s' % base64.b64encode('%s:%s' % (credentials[0], credentials[1]))
  }

def new_folder(credentials, folder_name):
  headers = _build_headers(credentials)
  data = urllib.urlencode({'name': folder_name})
  r = _make_request(baconfile_url + credentials[0] + '.json', data, headers)
  item = json.loads(r.read())
  return FolderItem(item)

"""Baconfile commandline"""

def show_help(page=''):
  if page == 'fetch':
    print 'Download a file from baconfile.com'
    print 'Usage: fetch <user> <path> [dest]'
    print '    user   -  owner of file being fetched'
    print '    path   -  path to file'
    print '    dest   -  where to save file [optional]'
    print 'Example: baconfile fetch john pictures/tree.jpg /home/me/pictures'
    print ''
  elif page == 'ls':
    print 'List infomation about files/folders'
    print 'Usage: ls <user> [folder]'
    print '    user   -  owner of files/folders to list'
    print '    folder -  folder to list [default: user\'s root folder]'
    print 'Example: baconfile ls john music'
    print ''
  elif page == 'recent':
    print 'Get listing of most recently added files'
    print 'Usage: recent'
    print ''
  elif page == 'mkdir':
    print 'Create a new folder on baconfile.com'
    print 'Usage: mkdir <folder>'
    print '    folder -  path + folder name'
    print 'Example: baconfile mkdir docs/papers'
    print ''
  else:
    print 'Baconfile commandline tool'
    print 'Usage: <command> [options]...'
    print 'Commands:'
    print '    fetch  -  download a file from baconfile.com'
    print '    ls     -  list infomation about files/folders'
    print '    recent -  list most recently added files'
    print 'Type just the command name to get more infomation.'

# query user for username and password
def get_credentials():
  print 'Baconfile.com login credentials required.:'
  print 'Username: ',
  username = raw_input()
  password = getpass()
  return username, password

def print_items(items):
  for i in items:
    if i.size is None:
      size = 'D'
    else:
      size = str(i.size)
    time = str(datetime.fromtimestamp(i.time_modified))
    print '%s  %s  %s  %s' % (time, i.type.rjust(6), size.rjust(8), i.name)

  print '  %i items' % len(items)

def cmd_fetch(user, path, dest=''):
  try:
    f = fetch_file(user, path)
    f.save_file(os.path.join(dest, f.name))
  except BaconfileError, e:
    print e
    exit(1)

def cmd_ls(user, folder=''):
  try:
    items = fetch_folder(user, folder)
    print_items(items)
  except BaconfileError, e:
    print e
    exit(1)

def cmd_recent():
  try:
    items = fetch_recent_files()
    print_items(items)
  except BaconfileError, e:
    print e
    exit(1)

def cmd_mkdir(folder_name):
  try:
    new_folder(get_credentials(), folder_name)
  except BaconfileError, e:
    print e
    exit(1)

if __name__ == '__main__':
  # Get command and args
  if len(sys.argv) < 2:
    show_help()
    exit(1)
  command = sys.argv[1]
  args = sys.argv[2:]

  # Call command
  try:
    if command == 'fetch':
      cmd_fetch(*args)
    elif command == 'ls':
      cmd_ls(*args)
    elif command == 'recent':
      cmd_recent()
    elif command == 'mkdir':
      cmd_mkdir(*args)
    else:
      print '%s invalid command!' % command
      show_help()
  except TypeError:
    # missing required arguments
    if len(args) > 0:
      print 'Missing required parameters!'
    show_help(command)
  except KeyboardInterrupt:
    print ''

