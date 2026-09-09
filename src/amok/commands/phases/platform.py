import subprocess
import shlex
import os
import logging

import amok.commands.build

from dataclasses import dataclass, field
from typing import override

from amok.commands.build import Phase
import yaml

@dataclass
class Platform_phase(Phase, name = "platform"):
	dnf_conf: str
	packages: list[str] = field(default_factory = list)
	
	@override
	def do_execute(self):
		logging.info("executing phase %d-%s", self.index, self.name)
		os.mkdir(self.resultdir / "data" / "rpms")
		with open(self.resultdir / "data" / "dnf.conf", "w") as ostream:
			ostream.write(self.dnf_conf)
		command = [
			"dnf", "-y", "--config", str(self.resultdir / "data" / "dnf.conf"), "download", "--resolve", "--alldeps", "--destdir", str(self.resultdir / "data" / "rpms"), *self.packages
		]
		with open(self.resultdir / "command", "w") as ostream:
			ostream.write(f"{shlex.join(command)}\n")
		with open(self.resultdir / "output.log", "w") as ostream:
			process = subprocess.run(command, text = True, stdin = None, stdout = ostream, stderr = ostream)
		with open(self.resultdir / "returncode", "w") as ostream:
			ostream.write(f"{process.returncode}\n")
			if process.returncode == 0:
				logging.info("phase %d-%s finished successfully", self.index, self.name)
			else:
				logging.info("phase %d-%s finished with an error: %d", self.index, self.name, process.returncode)
