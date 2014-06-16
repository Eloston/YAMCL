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

import copy
import hashlib
import pathlib

from yamcl.globals import URL
from yamcl.tools import FileTools

class LibraryManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj
        self.download_exclusive = True
        self.BASE_PATH = self.Launcher.ROOT_PATH.joinpath("lib")

        self.index_path = str(self.BASE_PATH.joinpath("index.json"))
        self.index = FileTools.read_json(self.index_path)

    def _flush_index(self):
        FileTools.write_json(self.index_path, self.index)

    def get_all_library_ids(self):
        return list(self.index.keys())

    def is_download_exclusive(self):
        return self.download_exclusive

    def set_download_exclusive(self, value):
        self.download_exclusive = value

    def is_library_existant(self, library_metadata):
        return library_metadata.get_id() in self.index

    def is_natives_existant(self, library_metadata, natives_extension):
        natives_directory = self.BASE_PATH.joinpath(*self.index[library_metadata.get_id()]["path"]).joinpath(natives_extension)
        return natives_directory.exists()

    def get_library_path(self, library_id):
        return pathlib.Path(*self.index[library_id]["path"])

    def _download_library(self, library_metadata):
        if self.download_exclusive and not library_metadata.current_system_supported():
            return
        if library_metadata.is_natives():
            if self.download_exclusive:
                all_extensions = [library_metadata.get_current_system_natives_extension()]
            else:
                all_extensions = library_metadata.get_all_natives_extensions()
            natives_list = all_extensions
        if self.is_library_existant(library_metadata):
            if library_metadata.is_natives():
                natives_list = list()
                for current_extension in all_extensions:
                    if not self.is_natives_existant(library_metadata, current_extension):
                        natives_list.append(current_extension)
                if natives_list == list():
                    return # Natives already exists
            else:
                return # Library already exists
        if library_metadata.is_natives():
            download_list = library_metadata.get_download_list(natives_list)
        else:
            download_list = library_metadata.get_download_list()
        for current_library in download_list:
            current_tries = 1
            while current_tries <= 3:
                correct_hash = current_library["hash"].url_object().read().decode("UTF-8")
                FileTools.write_object(str(self.BASE_PATH.joinpath(current_library["path"])), current_library["url"].url_object())
                hasher = hashlib.sha1()
                hasher.update(open(str(self.BASE_PATH.joinpath(current_library["path"])), mode="rb").read())
                if hasher.hexdigest() == correct_hash:
                    if library_metadata.is_natives():
                        natives_directory = self.BASE_PATH.joinpath(current_library["path"].parent.joinpath(current_library["natives_extension"]))
                        jar_path = str(self.BASE_PATH.joinpath(current_library["path"]))
                        FileTools.extract_jar_files(FileTools.get_jar_object(jar_path), str(natives_directory), library_metadata.get_natives_exclude())
                        FileTools.delete_and_clean(jar_path)
                    break
                else:
                    current_tries += 1
            if current_tries == 3:
                raise Exception("Failed to download library " + library_metadata.get_id()) # TODO: More appropriate exception
        self.index[library_metadata.get_id()] = dict()
        if library_metadata.is_natives():
            self.index[library_metadata.get_id()]["path"] = download_list[0]["path"].parent.parts
        else:
            self.index[library_metadata.get_id()]["path"] = download_list[0]["path"].parts

    def download_missing(self, library_metadata_list, progress_function=None):
        if not (progress_function == None):
            downloaded_count = 0
            progress_function("Downloading libraries", 0)
        for current_metadata in library_metadata_list:
            self._download_library(current_metadata)
            if not (progress_function == None):
                downloaded_count += 1
                progress_function("Downloading libraries", downloaded_count/len(library_metadata_list))
        self._flush_index()

    def get_platform_paths(self, library_metadata_list):
        libraries_dict = dict()
        libraries_dict["jars"] = list()
        libraries_dict["natives"] = list()
        for current_metadata in library_metadata_list:
            if current_metadata.current_system_supported():
                if not self.is_library_existant(current_metadata):
                    raise Exception("Library", current_metadata.get_id(), "does not exist") # TODO: More appropriate exception
                base_path = self.BASE_PATH.joinpath(self.get_library_path(current_metadata.get_id()))
                if current_metadata.is_natives():
                    current_extension = current_metadata.get_current_system_natives_extension()
                    if not self.is_natives_existant(current_metadata, current_extension):
                        raise Exception("Natives", current_extension, "for library", current_metadata.get_id(), "does not exist") # TODO: More appropriate exception
                    libraries_dict["natives"].append(str(base_path.joinpath(current_extension)))
                else:
                    libraries_dict["jars"].append(str(base_path))
        return libraries_dict

    def add_local(self, library_id, is_natives, source_paths, destination_path):
        '''
        source_paths is a list
        if regular library, then it should contain one string to a jar
        if natives, then it should contain paths to all natives directories
        Destination path is a path to a jar or directory (for regular or natives, respectively)
        '''
        if library_id in self.index:
            raise Exception("Library already exists") # TODO: More appropriate exception
        if isinstance(destination_path, list):
            final_path = self.BASE_PATH.joinpath(*destination_path)
        else:
            final_path = pathlib.Path(destination_path) # Assuming absolute
        if is_natives:
            for current_source in source_paths:
                try:
                    FileTools.copy(current_source, str(final_path.joinpath(FileTools.get_file_name(current_source))))
                except FileExistsError:
                    pass
        else:
            FileTools.copy(source_paths[0], str(final_path))
        self.index[library_id] = dict()
        self.index[library_id]["path"] = list(final_path.relative_to(self.BASE_PATH).parts)
        self._flush_index()

    def delete(self, library_id):
        if not library_id in self.index:
            raise Exception("Library is not existant") # TODO: More appropriate exception
        FileTools.delete_and_clean(str(self.BASE_PATH.joinpath(self.get_library_path(library_id))))
        del self.index[library_id]
        self._flush_index()

    def rename(self, current_library_id, new_library_id):
        if not current_library_id in self.index:
            raise Exception("Cannot rename library: " + current_library_id + " does not exist")
        if new_library_id in self.index:
            raise Exception("Cannot rename library: " + new_library_id + " already exists")
        self.index[new_library_id] = self.index[current_library_id]
        del self.index[current_library_id]
        self._flush_index()

    def get_unused_libraries(self, binary_parser_list):
        '''
        Returns a list of libraries not used in binary parsers 'binary_parser_list'
        '''
        used_library_ids = list()
        for binary_parser in binary_parser_list:
            for library_metadata in binary_parser.get_library_metadatas():
                if self.is_library_existant(library_metadata) and not (library_metadata.get_id() in used_library_ids):
                    used_library_ids.append(library_metadata.get_id())
        junk_library_ids = list()
        for installed_id in self.index:
            if not installed_id in used_library_ids:
                junk_library_ids.append(installed_id)
        return junk_library_ids

class LibraryMetadata:
    def __init__(self, launcher_obj, metadata_dict):
        self.Launcher = launcher_obj

        self.library_info = metadata_dict
        self.ARCH_KEY = "${arch}"

    def get_rules(self):
        '''
        Gets the platform rules (allow/disallow) for the library dictionary 'current_library_dict'
        '''
        tmp_rules = dict()
        for current in self.Launcher.PLATFORM_LIST:
            tmp_rules[current] = True

        if ("rules" in self.library_info):
            for current in self.Launcher.PLATFORM_LIST:
                tmp_rules[current] = False
            rules_list = self.library_info["rules"]
            for current_rule in rules_list:
                is_allow = current_rule["action"] == "allow"
                if ("os" in current_rule):
                    tmp_rules[current_rule["os"]["name"]] = is_allow
                else:
                    for current in self.Launcher.PLATFORM_LIST:
                        tmp_rules[current] = is_allow
        return tmp_rules

    def set_rules(self, os_rules):
        pass

    def current_system_supported(self):
        rules_dict = self.get_rules()
        current_family = self.Launcher.PlatformTools.get_os_family()
        return rules_dict[current_family]

    def is_natives(self):
        return "natives" in self.library_info

    def get_natives_exclude(self):
        return self.library_info["extract"]["exclude"]

    def get_id(self):
        return self.library_info["name"]

    def _path_by_id(self, natives_extension=str()):
        '''
        Works only for official library IDs
        Returns a list for a relative path
        '''
        parts = self.get_id().split(":")
        new_path = parts[0].split(".")
        del parts[0]
        new_path += parts
        if (len(natives_extension) > 0):
            new_path.append("-".join(parts) + "-" + natives_extension + ".jar")
        else:
            new_path.append("-".join(parts) + ".jar")
        return new_path

    def get_current_system_natives_extension(self):
        if not self.is_natives():
            raise Exception("Current library is not natives") # TODO: More appropriate exception
        if not self.current_system_supported():
            raise Exception("Current system not supported") # TODO: More appropriate exception
        current_family = self.Launcher.PlatformTools.get_os_family()
        current_natives_extension = self.library_info["natives"][current_family]
        if self.ARCH_KEY in current_natives_extension:
            current_natives_extension = current_natives_extension.replace(self.ARCH_KEY, self.Launcher.PlatformTools.get_java_arch())
        return current_natives_extension

    def get_all_natives_extensions(self):
        if not self.is_natives():
            raise Exception("Current library is not natives") # TODO: More appropriate exception
        natives_extension_list = list()
        for current_platform in self.library_info["natives"].keys():
            if self.get_rules()[current_platform]:
                current_extension = self.library_info["natives"][current_platform]
                if self.ARCH_KEY in current_extension:
                    natives_extension_list.append(current_extension.replace(self.ARCH_KEY, "32"))
                    natives_extension_list.append(current_extension.replace(self.ARCH_KEY, "64"))
                else:
                    natives_extension_list.append(current_extension)
        return natives_extension_list

    def get_download_list(self, natives_extension_list=None):
        '''
        Returns a list containing dictionaries in the form of:
        [
            {
                "url": URL(), # The JAR file
                "hash": URL(), # The SHA-1 sum file for the JAR
                "path": Path() # The relative path
            },
            ...
        ]
        There can be more than one pair if library is natives
        '''
        download_list = list()
        if self.is_natives():
            if natives_extension_list == None:
                raise Exception("No natives extensions specified for a natives library") # TODO: More appropriate exception
        else:
            natives_extension_list = [str()]
        for current_extension in natives_extension_list:
            relative_path = self._path_by_id(current_extension)
            info_dict = dict()
            info_dict["natives_extension"] = current_extension
            info_dict["url"] = URL(relative_path, URL.LIBRARIES)
            info_dict["path"] = pathlib.Path(*relative_path)
            hash_path = copy.copy(relative_path)
            hash_path[-1] += ".sha1"
            info_dict["hash"] = URL(hash_path, URL.LIBRARIES)
            download_list.append(info_dict)
        return download_list
