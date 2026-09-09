# TODO

import yaml

document = None

with open(document, "r") as istream:
	module = yaml.safe_load(istream)
	if module.get("document") != "modulemd":
		raise Exception(f"File {document} does not look like a modulemd file")
	yaml_module_data = module["data"]
	yaml_dependencies_buildrequires = {}
	for dependency in yaml_module_data.get("dependencies"):
		for name, values in dependency.get("buildrequires", {}).items():
			yaml_dependencies_buildrequires.setdefault(name, []).extend(values)
	yaml_buildopts_rpms_macros: str = yaml_module_data.get("buildopts", {}).get("rpms", {}).get("macros", "").strip()
	yaml_components_rpms = yaml_module_data.get("components", {}).get("rpms", {})
	print(yaml_buildopts_rpms_macros.splitlines())
	buildopts_rpms_macros: dict[str, str] = {}
	for line in yaml_buildopts_rpms_macros.splitlines():
		pos = line.find(" ")
		buildopts_rpms_macros[line[:pos].strip()[1:]] = line[pos + 1:].strip()
	phases_components = {}
	for rpm, rpm_data in yaml_components_rpms.items():
		phases_components.setdefault(rpm_data["buildorder"], []).append(rpm)
	print(sorted(phases_components))
