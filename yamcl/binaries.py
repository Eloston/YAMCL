'''
YAMCL is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

YAMCL is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with YAMCL.  If not, see {http://www.gnu.org/licenses/}.
'''

from yamcl.tools import FileTools
from yamcl.globals import URL
import yamcl.libraries

class BinaryManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj
        self.BASE_PATH = self.Launcher.ROOT_PATH.joinpath("bin")

        self.index_path = str(self.BASE_PATH.joinpath("index.json"))
        self.index = FileTools.read_json(self.index_path)

    def _flush_index(self):
        FileTools.write_json(self.index_path, self.index)

    def _get_version_index(self, version_id, version_type):
        version_count = 0
        for current_version in self.index:
            if current_version["name"] == version_id and current_version["type"] == version_type:
                return version_count
            else:
                version_count += 1
        return -1

    def version_exists(self, version_id, version_type):
        return self._get_version_index(version_id, version_type) > -1

    def get_installed_versions(self):
        installed_versions = dict()
        installed_versions["vanilla"] = list()
        installed_versions["custom"] = list()
        for current_version in self.index:
            installed_versions[current_version["type"]].append(current_version["name"])
        return installed_versions

    def get_paths(self, version_id, version_type):
        path_dict = dict()        
        path_dict["directory"] = self.BASE_PATH.joinpath(version_type+"/"+version_id)
        path_dict["jar"] = str(path_dict["directory"].joinpath(version_id+".jar"))
        path_dict["json"] = str(path_dict["directory"].joinpath(version_id+".json"))
        return path_dict

    def get_binary_parser(self, version_id, version_type):
        if not self.version_exists(version_id, version_type):
            raise Exception("Non-existant version") # TODO: More appropriate exception
        tmp_paths = self.get_paths(version_id, version_type)
        new_instance = BinaryParser(self.Launcher, tmp_paths["json"], (version_type == "custom"))
        return new_instance

    def get_binary_parser_list(self, exclude=None):
        exclude_specified = isinstance(exclude, dict)
        installed_versions = self.get_installed_versions()
        parser_list = list()
        for current_type in installed_versions:
            for current_id in installed_versions[current_type]:
                keep = False
                if exclude_specified:
                    try:
                        keep = not current_id in exclude[current_type]
                    except KeyError:
                        keep = True
                if keep:
                    parser_list.append(self.get_binary_parser(current_id, current_type))
        return parser_list

    def download_official(self, version_id):
        if self.version_exists(version_id, "vanilla"):
            raise Exception("Version " + version_id + " already exists") # TODO: More appropriate exception
        paths_dict = self.get_paths(version_id, "vanilla")

        FileTools.write_object(paths_dict["jar"], URL(["versions", version_id, version_id + ".jar"], URL.DOWNLOAD).url_object())
        FileTools.write_object(paths_dict["json"], URL(["versions", version_id, version_id + ".json"], URL.DOWNLOAD).url_object())

        current_listing = dict()
        current_listing["type"] = "vanilla"
        current_listing["name"] = version_id

        self.index.append(current_listing)

        self._flush_index()

    def install_custom(self, version_id, version_jar, version_json):
        if self.version_exists(version_id, "custom"):
            raise Exception("Version already exists") # TODO: More appropriate exception
        paths_dict = self.get_paths(version_id, "custom")
        FileTools.copy(version_jar, paths_dict["jar"])
        FileTools.copy(version_json, paths_dict["json"])

        current_listing = dict()
        current_listing["type"] = "custom"
        current_listing["name"] = version_id
        current_listing["notes"] = str()

        self.index.append(current_listing)

        self._flush_index()

    def custom_from_vanilla(self, vanilla_id, custom_id):
        if self.version_exists(custom_id, "custom"):
            raise Exception("Version already exists") # TODO: More appropriate exception
        if not self.version_exists(vanilla_id, "vanilla"):
            raise Exception("Vanilla version does not exist") # TODO: More appropriate exception
        vanilla_paths = self.get_paths(vanilla_id, "vanilla")
        custom_paths = self.get_paths(custom_id, "custom")
        FileTools.copy(vanilla_paths["jar"], custom_paths["jar"])
        FileTools.copy(vanilla_paths["json"], custom_paths["json"])

        current_listing = dict()
        current_listing["type"] = "custom"
        current_listing["name"] = custom_id
        current_listing["notes"] = str()

        self.index.append(current_listing)

        self._flush_index()

    def delete(self, version_id, version_type):
        if not self.version_exists(version_id, version_type):
            raise Exception("Version does not exist") # TODO: More appropriate exception
        index_count = 0
        for current_version in self.index:
            if current_version["type"] == version_type and current_version["name"] == version_id:
                break
            else:
                index_count += 1
        del self.index[index_count]
        self._flush_index()
        FileTools.delete_and_clean(str(self.get_paths(version_id, version_type)["directory"]))

    def rename(self, current_version_id, new_version_id):
        if not self.version_exists(current_version_id, "custom"):
            raise Exception("Cannot rename: " + current_version_id + " does not exist")
        if self.version_exists(new_version_id, "custom"):
            raise Exception("Cannot rename: " + new_version_id + " already exists")
        old_id_paths = self.get_paths(current_version_id, "custom")
        new_id_paths = self.get_paths(new_version_id, "custom")
        FileTools.add_missing_dirs(new_id_paths["jar"])
        for file_type in ["jar", "json"]:
            FileTools.move(old_id_paths[file_type], new_id_paths[file_type])
        FileTools.delete_and_clean(str(old_id_paths["directory"]))
        index_listing = self.index[self._get_version_index(current_version_id, "custom")]
        index_listing["name"] = new_version_id
        self._flush_index()

    def get_notes(self, version_id):
        if not self.version_exists(version_id, "custom"):
            raise Exception("Custom version does not exist") # TODO: More appropriate exception
        return self.index[self._get_version_index(version_id, "custom")]["notes"]

    def set_notes(self, version_id, new_notes):
        if not self.version_exists(version_id, "custom"):
            raise Exception("Custom version does not exist") # TODO: More appropriate exception
        self.index[self._get_version_index(version_id, "custom")]["notes"] = new_notes
        self._flush_index()

class BinaryParser:
    def __init__(self, launcher_obj, json_path, custom_bool):
        self.Launcher = launcher_obj
        self.is_custom = custom_bool

        self.info_path = json_path
        self.json_info = FileTools.read_json(json_path)

    def flush_info(self):
        FileTools.write_json(self.info_path, self.json_info)

    def get_library_parsers(self):
        parser_list = list()
        for library_dict in self.json_info["libraries"]:
            parser_list.append(yamcl.libraries.LibraryParser(self.Launcher, library_dict))
        return parser_list

    def get_minimum_version(self):
        return self.json_info["minimumLauncherVersion"]

    def is_compatible(self):
        return self.get_minimum_version() <= self.Launcher.COMPATIBLE_VERSION

    def get_id(self):
        return self.json_info["id"]

    def get_launch_class(self):
        return self.json_info["mainClass"]

    def get_arguments(self, values_dict):
        arguments_string = self.json_info["minecraftArguments"]
        for current_key in values_dict:
            arguments_string = arguments_string.replace("${" + current_key + "}", values_dict[current_key])
        return arguments_string

    def get_assets_id(self):
        if "assets" in self.json_info:
            return self.json_info["assets"]
        else:
            return "legacy"

    def delete_library(self, library_id):
        if not self.is_custom:
            raise Exception("Not a custom version") # TODO: More appropriate exception
        library_count = 0
        for current_library in self.json_info["libraries"]:
            if current_library["name"] == library_id:
                break
            else:
                library_count += 1
        del self.json_info["libraries"][library_count]
        self.flush_info()

    def add_library(self, library_id, rules_dict=None, natives_dict=None):
        if not self.is_custom:
            raise Exception("Not a custom version") # TODO: More appropriate exception
        library_dict = dict()
        library_dict["name"] = library_id
        if not natives_dict == None:
            library_dict["natives"] = natives_dict
        if not rules_dict == None:
            rules_list = list()
            for current_platform in rules_dict:
                current_rule = dict()
                current_rule["os"] = dict()
                current_rule["os"]["name"] = current_platform
                if rules_dict[current_platform]:
                    current_rule["action"] = "allow"
                else:
                    current_rule["action"] = "disallow"
                rules_list.append(current_rule)
            library_dict["rules"] = rules_list
        self.json_info["libraries"].append(library_dict)
        self.flush_info()
