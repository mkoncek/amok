#!/usr/bin/python3

import argparse
import tempfile
import os
import sys
import logging

from pathlib import Path

import amok.commands
import amok.commands.init
import amok.commands.plan
import amok.commands.build

VERSION = "0.0.1"

if __name__ == '__main__':
	arg_parser = argparse.ArgumentParser(
		prog = "amok",
		description = "Run a sequence of Mock builds",
	)
	arg_parser.add_argument("-v", "--version", action = "version", version = VERSION)
	arg_parser.add_argument("-d", "--debug", action = "store_true")
	arg_parser.add_argument("-w", "--workspace", type = Path)
	
	subparsers = arg_parser.add_subparsers(dest = "command")
	for name, cmd_class in amok.commands.Command.registry().items():
		sub = subparsers.add_parser(name)
		cmd_class.setup(sub)
		sub.set_defaults(command_class = cmd_class)
	args = arg_parser.parse_args()
	
	if args.debug:
		logging.getLogger().setLevel(logging.DEBUG)
	else:
		logging.getLogger().setLevel(logging.INFO)
	logging.debug("Amok version: %s", VERSION)
	
	if hasattr(args, "command_class"):
		cmd = args.command_class(args)
		cmd.execute()
	else:
		logging.error("no command specified")
		arg_parser.print_help()
		sys.exit(1)
