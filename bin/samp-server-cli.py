#!/usr/bin/env python
#
# Copyright (c) 2012-2013 Zeex
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import argparse
import itertools
import os
import platform
import random
import string
import subprocess
import sys
import threading

def generate_password(size=10, chars=string.ascii_letters + string.digits):
  return ''.join(random.choice(chars) for x in range(size))

def parse_options(args):
  parser = argparse.ArgumentParser(
    description='A command line interface to SA:MP server',
    fromfile_prefix_chars='@',
  )

  argument = lambda *args, **kwargs: parser.add_argument(*args, **kwargs)

  argument('-a', '--announce', dest='announce',
           action='store_const', const=1, default=0,
           help='announce to server masterlist')

  argument('-b', '--bind', dest='bind', metavar='address',
           help='bind to specific IP address')

  argument('--chatlogging', dest='chatlogging',
           action='store_const', const=1, default=0,
           help='enable logging of in-game chat')

  argument('-c', '--command', dest='command',
           nargs='+', metavar=('cmd', 'args'),
           help='override server startup command (path to server executable '
                'by default)')

  argument('-D', '--debug', dest='debug',
           nargs=argparse.REMAINDER,
           help='run server under debugger')

  argument('-e', '--exec', dest='exec',
           metavar='filename',
           help='load options from file')

  argument('-E', '--extra', dest='extra',
           nargs='+', metavar='name value', 
           help='additional server.cfg options (order may change)')

  argument('-f', '--filterscript', dest='filterscripts',
           metavar='name/path', action='append',
           help='add a filter script; multiple occurences of this option are '
                'allowed')

  argument('-g', '-g0', '--gamemode', '--gamemode0', dest='gamemode0',
           metavar='name/path', required=True,
           help='set startup game mode (mode #0)')

  for i in range(1, 10):
    argument('-g%d' % i, '--gamemode%d' % i, dest='gamemode%d' % i,
             metavar='name/path',
             help='set game mode #%d' % i)

  argument('--gamemodetext', dest='gamemodetext',
           metavar='"My Game Mode"',
           help='set game mode text (shown in server browser)')

  argument('-n', '--hostname', dest='hostname',
           metavar='"My SA-MP server"',
           help='set host name (shown in server browser)')

  argument('--incar-rate', dest='incar_rate',
           metavar='ms',
           help='set player data update rate while in a vehicle')

  argument('-l', '--lanmode', dest='lanmode',
           action='store_const', const=1, default=0,
           help='enable LAN mode')

  argument('-L', '--local', dest='local',
           action='store_true', default=False,
           help='run in current directory (same as if you pass "--workdir .")')

  argument('-Q', '--logqueries', dest='logqueries',
           action='store_const', const=1, default=0,
           help='enable logging of queries sent to the server')

  argument('--logtimeformat', dest='logtimeformat',
           metavar='format',
           help='set log timestamp format')

  argument('-m', '--mapname', dest='mapname',
           metavar='name',
           help='set map name (shown in server browser)')

  argument('--maxnpc', dest='maxnpc', metavar='number',
           type=int, default=0,
           help='set max. number of NPCs (bots)')

  argument('--maxplayers', dest='maxplayers',
           metavar='number', type=int, default=500,
           help='set max. number of players')

  argument('--myriad', dest='myriad',
           action='store_const', const=1, default=0,
           help='??')

  argument('--nosign', dest='nosign',
           action='store_const', const=1, default=0,
           help='??')
           
  argument('--no-launch', dest='no_launch',
           action='store_const', const=True, default=False,
           help='don\'t launch the server, just write server.cfg')

  argument('--onfoot-rate', dest='onfoot_rate',
           metavar='ms',
           help='set player data update rate while walking/running')

  argument('-o', '--output', dest='output',
           action='store_const', const=1, default=0,
           help='enable console output (Linux only)')

  argument('-P', '--password', dest='password',
           nargs='?', metavar='password', const=generate_password(),
           help='set server password')

  argument('-d', '--plugin', dest='plugins',
           metavar='name/path', action='append',
           help='add a plugin; multiple occurences of this option are allowed')

  argument('-p', '--port', dest='port',
           metavar='number', type=int, default=7777,
           help='set server listen port')
  
  argument('-q', '--query', dest='query',
           action='store_const', const=1, default=0,
           help='allow querying server info from outside world (e.g. server '
                'browser)')

  argument('-r', '--rcon', dest='rcon',
           action='store_const', const=1, default=0,
           help='enable RCON (Remote CONsole)')

  argument('-R', '--rcon-password', dest='rcon_password',
           metavar='password',
           help='set RCON password (implies --rcon)')

  argument('-s', '--servdir', dest='servdir',
           metavar='path',
           help='set server\'s root directory (current directory by default); '
                'not necesssary if you use -c')

  argument('--sleep', dest='sleep',
           metavar='ms',
           help='set server sleep time')

  argument('--stream-distance', dest='stream_distance',
           metavar='float',
           help='set stream distance')

  argument('--stream-rate', dest='stream_rate',
           metavar='ms',
           help='set stream rate')

  argument('-t', '--timestamp', dest='timestamp',
           action='store_const', const=1, default=0,
           help='enable timestamps in log')

  argument('-T', '--timeout', dest='timeout',
           metavar='sec', type=float,
           help='limit server run time')

  argument('--weapon-rate', dest='weapon_rate',
           metavar='ms',
           help='set player data update rate while firing a weapon')

  argument('-u', '--weburl', dest='weburl',
           metavar='url',
           help='set contact website URL')

  argument('-w', '--workdir', dest='workdir',
           metavar='path',
           help='set working directory (server directory by default)')

  return vars(parser.parse_args(args))
  
def is_windows():
  system = platform.system()
  return system == 'Windows' or system.startswith('CYGWIN_NT')

def is_linux():
  system = platform.system()
  return system == 'Linux'

def read_config(filename):
  options = {}
  with open(filename, 'r') as file:
    for line in file.readlines():
      try:
        name, value = string.split(line.strip(), maxsplit=1)
        options[name] = value
      except ValueError:
        name = line.strip()
        if len(name) > 0:
          options[name] = ''
  return options

def write_config(filename, options):
  with open(filename, 'w') as file:
    for name, value in options.items():
      if value is not None:
        if len(str(value)) > 0:
          file.write('%s %s\n' % (name, value))
        else:
          file.write('%s\n' % name)

def group(n, iterable, padvalue=None):
    "group(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return itertools.izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)

def main(argv):
  options = parse_options(argv[1:])

  servdir = options.pop('servdir')
  if servdir is None:
    servdir = os.environ.get('SAMP_SERVER_ROOT')
    if servdir is None:
      servdir = os.getcwd()
  if not os.path.isabs(servdir):
    servdir = os.path.abspath(servdir)

  local = options.pop('local')
  if local:
    workdir = os.getcwd()
  else:
    workdir = options.pop('workdir')
    if workdir is None:
      workdir = servdir
    else:
      if not os.path.exists(workdir):
        os.mkdir(workdir)

  command = options.pop('command')
  if command is None:
    exe = os.environ.get('SAMP_SERVER')
    if exe is None:
      if is_windows():
        exe = 'samp-server.exe'
      else:
        exe = 'samp03svr'
    command = [os.path.join(servdir, exe)]

  extra = options.pop('extra')
  if extra is not None:
    extra_options = dict(group(2, extra))
    options.update(extra_options)

  exec_file = options.pop('exec')
  if exec_file is not None:
    exec_options = read_config(exec_file)
    options.update(exec_options)

  rcon_password = options['rcon_password']
  if rcon_password is not None:
    options['rcon'] = 1
  else:
    options['rcon_password'] = generate_password()

  plugins = options['plugins'] 
  if plugins is not None:
    if is_windows():
      ext = '.dll'
    else:
      ext = '.so'
    for i, p in enumerate(plugins):
      if not p.lower().endswith(ext):
        plugins[i] += ext

  dirs = { 'filterscripts': 'filterscripts',
           'plugins':       'plugins',
         }
  for i in range(0, 10):
    dirs['gamemode%d' % i] = 'gamemodes'

  for name, dir in dirs.items():
    dir = os.path.join(workdir, dir)
    if not os.path.exists(dir):
      os.mkdir(dir)
    values = options[name]
    if values is None:
      continue
    if not type(values) is list:
      values = [values]
    if values is not None:
      for i, v in enumerate(values):
        if not os.path.isabs(v) and not v.startswith('.'):
          # If this is a relative path that does not start with a '.' leave it
          # as is. This is how you typically write script names in server.cfg.
          continue
        else:
          # Otherwise make it relative to the corresponding directory.
          values[i] = os.path.relpath(v, dir)
      options[name] = '%s' % ' '.join(values)

  debug = options.pop('debug')
  if debug is not None:
    if is_linux():
      command = ['gdb'] + debug + ['--args'] + command
    elif is_windows():
      command = ['windbg'] + debug + command

  no_launch = options.pop('no_launch')
    
  server_cfg = os.path.join(workdir, 'server.cfg')
  write_config(server_cfg, options)
  
  if not no_launch:
    os.chdir(workdir)
    try:
      timeout = options.pop('timeout')
      server = subprocess.Popen(command)
      if timeout is not None:
        term_timer = threading.Timer(timeout, server.terminate)
        term_timer.start()
        server.wait()
        term_timer.cancel()
      else:
        server.wait()
      sys.exit(server.returncode)
    except KeyboardInterrupt:
      sys.exit(0)

if __name__ == '__main__':
  main(sys.argv)