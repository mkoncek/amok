import argparse

from amok.util.abc_named import ABC_named

from abc import abstractmethod

class Command(ABC_named):
	def __init__(self, args: argparse.Namespace) -> None:
		self.args = args
	
	@staticmethod
	def setup(subparser: argparse.ArgumentParser) -> None:
		"""Register command-specific arguments on the subparser."""
		pass
	
	@abstractmethod
	def execute(self) -> None:
		pass
