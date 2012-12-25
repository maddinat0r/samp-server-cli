#!/usr/bin/env python

import argparse
import os
import random
import string
import subprocess
import sys

def generate_password(size=10, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

def get_arguments(args):
	parser = argparse.ArgumentParser()

	parser.add_argument('-announce', type=int, choices=[0, 1], default=0, help='Toggle announcement')
	parser.add_argument('-bind', metavar='address', help='Bind to specific IP address')
	parser.add_argument('-filterscripts', metavar='path', nargs='*', help='List of filter scripts to be loaded')
	parser.add_argument('-gamemode0', metavar='path', required=True, help='Main game mode')
	for i in range(1, 10):
		parser.add_argument('-gamemode%d' % i, metavar='path', help='Game mode #%d' % i)
	parser.add_argument('-gamemodetext', metavar='"My Game Mode"', help='Game mode text (shown in server browser)')
	parser.add_argument('-hostname', metavar='"My SA-MP server"', help='Host name (shown in server browser)')
	parser.add_argument('-lanmode', type=int, choices=[0, 1], default=0, help='Toggle LAN mode')
	parser.add_argument('-logtimeformat', metavar='format', help='Format of time stamps in log')
	parser.add_argument('-mapname', metavar='name', help='Map name (shown in server browser)')
	parser.add_argument('-maxplayers', metavar='number', type=int, default=1, help='Max. number of players')
	parser.add_argument('-maxnpc', metavar='number', type=int, default=0, help='Max. number of NPCs (bots)')
	parser.add_argument('-output', type=int, choices=[0, 1], default=0, help='Toggle console output')
	parser.add_argument('-password', metavar='password', help='Server password')
	parser.add_argument('-serverdir', metavar='path', default='', help='Path to server root')
	parser.add_argument('-plugins', metavar='path', nargs='*', help='List of plugins to be loaded')
	parser.add_argument('-port', metavar='number', type=int, default=7777, help='Server port')
	parser.add_argument('-query', type=int, choices=[0, 1], default=0)
	parser.add_argument('-rcon', type=int, choices=[0, 1], default=0, help='Toggle RCON (Remote CONsole)')
	parser.add_argument('-rcon_password', metavar='password', default=generate_password(), help='RCON password')
	parser.add_argument('-timestamp', type=int, choices=[0, 1], default=1, help='Show time stamps in log')
	parser.add_argument('-weburl', metavar='url', help='Website URL')
	parser.add_argument('-workingdir', metavar='path', default='.', help='Working directory')

	args = parser.parse_args(args)
	return vars(args)

def write_config(filename, options):
	file = open(filename, 'w')
	for name, value in options.items():
		if value is not None:
			file.write('%s %s\n' % (name, value))
	file.close()

def mkdir(path):
	if not os.path.exists(path):
		os.mkdir(path)

def run(options):
	working_dir = options['workingdir']
	if not os.path.exists(working_dir):
		os.mkdir(working_dir)

	dirs = {
		'filterscripts': 'filterscripts',
		'plugins': 'plugins',
	}
	for i in range(0, 10):
		dirs['gamemode%d' % i] = 'gamemodes'

	for name, dir in dirs.items():
		dir = os.path.join(working_dir, dir)
		values = options[name]
		if values is None:
			continue
		if not type(values) is list:
			values = [values]
		if values is not None:
			for i, v in enumerate(values):
				values[i] = os.path.relpath(v, dir)
			options[name] = '%s' % ' '.join(values)

	server_dir = os.path.abspath(options['serverdir'])
	if os.name == 'nt':
		server_exe = 'samp-server.exe'
	else:
		server_exe = 'samp03svr'
	server_path = os.path.join(server_dir, server_exe)

	write_config(os.path.join(working_dir, 'server.cfg'), options)

	mkdir(os.path.join(working_dir, 'gamemodes'))
	mkdir(os.path.join(working_dir, 'filterscripts'))

	os.chdir(working_dir)
	subprocess.call(server_path)

if __name__ == '__main__':
	run(get_arguments(sys.argv[1:]))
