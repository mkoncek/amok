import os
import argparse
import logging
import dataclasses
import shutil

from dataclasses import dataclass, field
from pathlib import Path
from typing import override
from ruamel.yaml import YAML

from amok.commands import Command
from amok.commands.phases.platform import Platform_phase

class Plan_command(Command, name = "plan"):
	@override
	def execute(self) -> None:
		with open(self.args.workspace / "amok.yaml", "r") as istream:
			self.config = YAML(typ = "safe", pure = True).load(istream)
		platform = self.config["platform"]
		platform_phase = Platform_phase(packages = platform["packages"], dnf_conf = '''\
[main]
gpgcheck=0
reposdir=/dev/null
install_weak_deps=0
protected_packages=""
assumeyes=1

''')
		for repo_name, repo_url in platform["repos"].items():
			platform_phase.dnf_conf += f'''\
[{repo_name}]
name={repo_name}
baseurl={repo_url}
module_hotfixes=1

'''
		self.plan = {
			"phases": [
				{"platform": dataclasses.asdict(platform_phase)}
			]
		}
		plan_file = self.args.workspace / "target" / "plan.yaml"
		logging.info("writing build plan to %s", plan_file)
		with open(plan_file, "w") as ostream:
			yaml = YAML(typ = "safe", pure = True)
			yaml.default_flow_style = False
			yaml.sort_base_mapping_type_on_output = False
			yaml.dump(self.plan, ostream)
