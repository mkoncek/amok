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

@dataclass
class Template():
	lookaside_url: str = ""
	distgit_rpm_url: str = ""
	distgit_module_url: str = ""
	repos: dict[str, str] = field(default_factory = dict)

def get_template(name: str, version: str) -> Template:
	return {
		"fedora": Template(
			lookaside_url = "https://src.fedoraproject.org/lookaside/pkgs",
			distgit_rpm_url = "https://src.fedoraproject.org/rpms",
			distgit_module_url = "https://src.fedoraproject.org/modules",
			repos = {
				"Everything": f"https://dl.fedoraproject.org/pub/fedora/linux/development/{version}/Everything/x86_64/os"
			},
		),
	}[name]

class Init_command(Command, name = "init"):
	@override
	@staticmethod
	def setup(subparser: argparse.ArgumentParser) -> None:
		subparser.add_argument(
			"-t", "--template",
			default = None,
			help = "Template to initialize from",
		)
		subparser.add_argument(
			"-f", "--force",
			action = "store_true",
			help = "Force re-initialization of the workspace",
		)
	
	@override
	def execute(self) -> None:
		if self.args.workspace is None:
			self.args.workspace = Path(tempfile.mkdtemp(dir = amok.DEFAULT_WORKSPACE_DIR))
		elif not self.args.workspace.exists():
			os.makedirs(self.args.workspace)
			logging.debug("created directory at %s", self.args.workspace)
		if self.args.workspace.exists() and not self.args.workspace.is_dir():
			raise Exception(f"workspace directory {self.args.workspace} exists and it not a directory")
		if self.args.workspace.is_dir() and not self.args.force:
			logging.debug("workspace directory %s already exists", self.args.workspace)
		else:
			if self.args.force:
				logging.debug("re-initialzing worskapce %s", self.args.workspace)
				shutil.rmtree(self.args.workspace)
			os.mkdir(self.args.workspace)
			logging.info("created workspace directory %s", self.args.workspace)
			if self.args.template is None:
				template = Template()
			else:
				template_list = self.args.template.split(":")
				template_os = template_list[0]
				template_version = None
				if len(template_list) == 2:
					template_version = template_list[1]
				if template_os == "fedora" and template_version is None:
					template_version = "rawhide"
				template = get_template(template_os, template_version)
			with open(self.args.workspace / "amok.yaml", "w") as ostream:
				yaml = YAML(typ = "safe", pure = True)
				yaml.default_flow_style = False
				yaml.sort_base_mapping_type_on_output = False
				yaml.dump({
					"lookaside_url": template.lookaside_url,
					"distgit_rpm_url": template.distgit_rpm_url,
					"distgit_module_url": template.distgit_module_url,
					"platform": {
						"repos": template.repos,
						"packages": ["rpm-build"],
					},
					"phases": [],
				}, ostream)
			os.mkdir(self.args.workspace / "rpms")
			os.mkdir(self.args.workspace / "modules")
			os.mkdir(self.args.workspace / "tests")
			os.mkdir(self.args.workspace / "target")
