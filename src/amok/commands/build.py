import argparse
import os
import shutil
import logging

from abc import abstractmethod
from typing import Any, override
from ruamel.yaml import YAML
from dataclasses import dataclass

from amok.util.abc_named import ABC_named
from amok.commands import Command

class Phase(ABC_named):
	def bind(self, command: "Build_command", index: int) -> Phase:
		self.command = command
		self.index = index
		self.resultdir = self.command.args.workspace / "target" / f"{index}-{self.name}"
		return self
	
	def execute(self):
		try:
			with open(self.resultdir / "returncode", "r") as istream:
				try:
					if int(istream.read()) == 0:
						logging.info("phase %d-%s already finished", self.index, self.name)
						return
				except ValueError:
					pass
		except FileNotFoundError:
			pass
		try:
			shutil.rmtree(self.resultdir)
		except FileNotFoundError:
			pass
		os.mkdir(self.resultdir)
		os.mkdir(self.resultdir / "data")
		self.do_execute()
	
	@abstractmethod
	def do_execute(self):
		pass

class Build_command(Command, name = "build"):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config: dict[Any, Any] = {}
		self.phases: list[Phase] = []
	
	@override
	def execute(self) -> None:
		with open(self.args.workspace / "target" / "plan.yaml", "r") as istream:
			yaml = YAML(typ = "safe", pure = True).load(istream)
			for index, phase_dict in enumerate(yaml["phases"]):
				phase_name, phase_data = phase_dict.popitem()
				Phase.registry()[phase_name](**phase_data).bind(self, index).execute()
