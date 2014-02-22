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

from yamcl.globals import DataPath, URL
import yamcl.libraries

class BinaryManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj
        self.BASE_PATH = DataPath("bin")

        self.index_path = str(self.BASE_PATH + DataPath("index.json"))
        self.index = self.Launcher.FileTools.read_json(self.index_path)

    def flush_index(self):
        self.Launcher.FileTools.write_json(self.index_path, self.index)

    def version_exists(self, version_id, version_type):
        for current_version in self.index:
            if current_version["name"] == version_id and current_version["type"] == version_type:
                return True
        return False

    def get_paths(self, version_id, version_type):
        path_dict = dict()        
        path_dict["directory"] = self.BASE_PATH + DataPath(version_type+"/"+version_id)
        path_dict["jar"] = str(path_dict["directory"] + DataPath(version_id+".jar"))
        path_dict["json"] = str(path_dict["directory"] + DataPath(version_id+".json"))
        return path_dict

    def get_binary_parser(self, version_id, version_type):
        if not self.version_exists(version_id, version_type):
            raise Exception("Non-existant version") # TODO: More appropriate exception
        tmp_paths = self.get_paths(version_id, version_type)
        new_instance = BinaryParser(self.Launcher, tmp_paths["json"])
        return new_instance

    def download_official(self, version_id):
        if self.version_exists(version_id, "vanilla"):
            raise Exception("Version " + version_id + " already exists") # TODO: More appropriate exception
        paths_dict = self.get_paths(version_id, "vanilla")

        self.Launcher.FileTools.write_object(paths_dict["jar"], URL(["versions", version_id, version_id + ".jar"], URL.DOWNLOAD).url_object())
        self.Launcher.FileTools.write_object(paths_dict["json"], URL(["versions", version_id, version_id + ".json"], URL.DOWNLOAD).url_object())

        current_listing = dict()
        current_listing["type"] = "vanilla"
        current_listing["name"] = version_id

        self.index.append(current_listing)

        self.flush_index()

    def install_custom(self, version_id, version_path, version_json):
        pass

    def custom_from_vanilla(self, vanilla_id, custom_id):
        pass

class BinaryParser:
    def __init__(self, launcher_obj, json_path):
        self.Launcher = launcher_obj

        self.json_info = self.Launcher.FileTools.read_json(json_path)

    def get_library_parsers(self):
        parser_list = list()
        for library_dict in self.json_info["libraries"]:
            parser_list.append(yamcl.libraries.LibraryParser(self.Launcher, library_dict))
        return parser_list

    def is_compatible(self):
        return self.json_info["minimumLauncherVersion"] <= self.Launcher.COMPATIBLE_VERSION

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
