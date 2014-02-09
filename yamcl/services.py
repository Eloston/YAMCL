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

class BinaryManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

        self.versions_json = None
        self.index = self.Launcher.FileTools.read_json(self.Launcher.FileTools.get_full_path(["bin", "index.json"]))

    def download_versions(self):
        '''
        Downloads the latest versions.json from the official servers
        '''
        tmp_file_object = self.Launcher.NetworkTools.get_url_object(self.Launcher.NetworkTools.VERSIONS_JSON_URL)
        versions_path = self.Launcher.FileTools.get_full_path(["bin", "versions.json"])
        self.Launcher.FileTools.write_object(versions_path, tmp_file_object)

        self.versions_json = None
        self.get_versions()

    def get_versions(self):
        '''
        Returns the object form of the versions.json file. If it is not loaded, it will be automatically loaded.
        '''
        if (self.versions_json is None):
            versions_path = self.Launcher.FileTools.get_full_path(["bin", "versions.json"])
            self.versions_json = self.Launcher.FileTools.read_json(versions_path)
        return self.versions_json

    def flush_index(self):
        '''
        Writes current binary index in memory to the YAMCL data directory
        '''
        self.Launcher.FileTools.write_json(self.Launcher.FileTools.get_full_path(["bin", "index.json"]), self.index)

    def download_official_version_id(self, version_id):
        '''
        Downloads a Minecraft jar and json file from the official servers via an ID
        '''
        jar_path = self.Launcher.FileTools.get_full_path(["bin", "vanilla", version_id, version_id + ".jar"])
        json_path = self.Launcher.FileTools.get_full_path(["bin", "vanilla", version_id, version_id + ".json"])

        self.Launcher.FileTools.write_object(jar_path, self.Launcher.NetworkTools.get_url_object(self.Launcher.NetworkTools.DOWNLOAD_URL + "versions/" + version_id + "/" + version_id + ".jar"))
        self.Launcher.FileTools.write_object(json_path, self.Launcher.NetworkTools.get_url_object(self.Launcher.NetworkTools.DOWNLOAD_URL + "versions/" + version_id + "/" + version_id + ".json"))

        current_listing = dict()
        current_listing["type"] = "vanilla"
        current_listing["name"] = version_id

        self.index.append(current_listing)

        self.flush_index()

    def get_version_file_paths(self, version_name, version_type):
        '''
        Returns a list containing the absolute path to the jar, and the path to the json
        '''
        tmp_current_path = ["bin", version_type, version_name]
        return [self.Launcher.FileTools.get_full_path(tmp_current_path + [version_name + ".jar"]), self.Launcher.FileTools.get_full_path(tmp_current_path + [version_name + ".json"])]

    def delete_version(self, version_name, version_type):
        '''
        Deletes a Minecraft version specfied by name 'version_name' and type 'version_type'
        '''
        pass

class LibraryManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

        self.index = self.Launcher.FileTools.read_json(self.Launcher.FileTools.get_full_path(["lib", "index.json"]))

    def flush_index(self):
        '''
        Writes current library index in memory to the YAMCL data directory
        '''
        self.Launcher.FileTools.write_json(self.Launcher.FileTools.get_full_path(["lib", "index.json"]), self.index)

    def official_id_to_path(self, library_id, natives_extension=""):
        '''
        Geneates a list containing the path elements that leads to the library file on the Mojang servers, and for storing library files locally. If native_extension is not blank, will append the native extension as well. (e.g. natives-windows-32)
        '''
        parts = library_id.split(":")
        new_path = parts[0].split(".")
        del parts[0]
        new_path += parts
        if (len(natives_extension) > 0):
            new_path.append("-".join(parts) + "-" + natives_extension + ".jar")
        else:
            new_path.append("-".join(parts) + ".jar")
        return new_path

    def get_library_rules(self, current_library_dict):
        '''
        Gets the platform rules (allow/disallow) for the library dictionary 'current_library_dict'
        '''
        tmp_rules = dict()
        for current in self.Launcher.PLATFORM_LIST:
            tmp_rules[current] = True

        if ("rules" in current_library_dict):
            for current in self.Launcher.PLATFORM_LIST:
                tmp_rules[current] = False
            rules_list = current_library_dict["rules"]
            for current_rule in rules_list:
                is_allow = current_rule["action"] == "allow"
                if ("os" in current_rule):
                    tmp_rules[current_rule["os"]["name"]] = is_allow
                else:
                    for current in self.Launcher.PLATFORM_LIST:
                        tmp_rules[current] = is_allow
        return tmp_rules

    def delete_libraries(self, library_id_list):
        '''
        Deletes libraries specified by the library ID list 'library_id_list'. Directories that have become empty because of the deletion of a library will be removed.
        '''
        # TODO: use os.removedirs(path) to delete empty directories
        # TODO: use shutil.rmtree() to delete jar or natives, but not clear empty directories
        pass

    def delete_unused_libraries(self):
        '''
        Deletes all libraries that are not being used by a Minecraft version.
        '''
        pass

    def extract_natives_jar(self, library_id, natives_extension):
        '''
        Extracts the natives jar file into its proper directory, and deletes the jar file
        '''
        pass

    def download_missing_official_libraries(self, version_id, progress_function=None):
        '''
        Downloads the libraries that are missing for the official binary 'version_id'

        'progress_function' is a function that is called whenever the progress updates. Parameters include 'status' and 'percentage', where 'status' is a string describing the current progress, and 'percentage' is the current progress from 0.0 to 1.0
        '''
        version_libraries = self.Launcher.FileTools.read_json(self.Launcher.BinaryManager.get_version_file_paths(version_id, "vanilla")[1])["libraries"]

        natives_libraries = dict()
        regular_libraries = dict()

        if not (progress_function == None):
            progress_function("Generating library URLs", 0)

        for current_library in version_libraries:
            is_new_library = True
            for existing_library_dict in self.index:
                if (current_library["name"] == existing_library_dict["name"]):
                    is_new_library = False
                    break
            if (is_new_library):
                library_listing = dict()
                library_listing["name"] = current_library["name"]
                if ("natives" in current_library):
                    library_listing["path"] = self.official_id_to_path(current_library["name"])
                    del library_listing["path"][-1]
                    library_listing["natives"] = list()
                    for natives_platform in current_library["natives"]:
                        if (self.get_library_rules(current_library)[natives_platform]):
                            if ("${arch}" in current_library["natives"][natives_platform]):
                                natives_extensions = [current_library["natives"][natives_platform].replace("${arch}", "32"), current_library["natives"][natives_platform].replace("${arch}", "64")]
                                library_listing["natives"].append(natives_platform + "-${arch}")
                            else:
                                natives_extensions = [current_library["natives"][natives_platform]]
                                library_listing["natives"].append(natives_platform)
                            for current_extension in natives_extensions:
                                path_list = self.official_id_to_path(current_library["name"], current_extension)
                                natives_libraries[self.Launcher.NetworkTools.LIBRARIES_URL + '/'.join(path_list)] = self.Launcher.FileTools.get_full_path(["lib"] + path_list)
                else:
                    path_list = self.official_id_to_path(current_library["name"])
                    library_listing["path"] = path_list
                    regular_libraries[self.Launcher.NetworkTools.LIBRARIES_URL + '/'.join(path_list)] = self.Launcher.FileTools.get_full_path(["lib"] + path_list)
                self.index.append(library_listing)

        # Downloading libraries
        libraries_downloaded = 0
        total_libraries = len(natives_libraries)
        for current_url in natives_libraries:
            url_object = self.Launcher.NetworkTools.get_url_object(current_url)
            self.Launcher.FileTools.write_object(natives_libraries[current_url], url_object)
            libraries_downloaded += 1
            if not (progress_function == None):
                progress_function("Downloading natives", (libraries_downloaded/total_libraries)*0.5)

        libraries_downloaded = 0
        total_libraries = len(regular_libraries)
        for current_url in regular_libraries:
            url_object = self.Launcher.NetworkTools.get_url_object(current_url)
            self.Launcher.FileTools.write_object(regular_libraries[current_url], url_object)
            libraries_downloaded += 1
            if not (progress_function == None):
                progress_function("Downloading libraries", (libraries_downloaded/total_libraries)*0.5+0.5)

        if not (progress_function == None):
            progress_function("Writing library index", 1)
        self.flush_index()

class ProfileManager:
    def __init__(self, launcher_obj, java_command):
        self.Launcher = launcher_obj
        if (java_command == str()):
            # TODO: Read registry, do whatever on Mac?, otherwise deefault to "java"
            self.java_command = "java"
        else:
            self.java_command = java_command

class ProfileInstance:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

class AssetManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

    def get_binary_assets_id(self, version_id):
        '''
        Get the assets ID from a binary version 'version_id'
        '''
        current_asset_id = "legacy"
        version_info = version_libraries = self.Launcher.FileTools.read_json(self.Launcher.BinaryManager.get_version_file_paths(version_id, "vanilla")[1])
        if ("assets" in version_info):
            current_assets_id = version_info["assets"]
        return current_assets_id

    def download_asset_index(self, asset_id):
        '''
        Downloads the JSON asset index specified by 'asset_id'
        '''
        asset_url_object = self.Launcher.NetworkTools.get_url_object(self.Launcher.NetworkTools.INDEXES_URL + asset_id + ".json")
        asset_index_path = self.Launcher.FileTools.get_full_path(["bin", "assets", "indexes", asset_id + ".json"])
        self.Launcher.FileTools.write_object(asset_index_path, asset_url_object)

    def download_missing_assets(self, asset_id, progress_function=None):
        '''
        Downloads assets specified in 'asset_id' but are not already downloaded
        '''
        asset_info = self.Launcher.FileTools.read_json(self.Launcher.FileTools.get_full_path(["bin", "assets", "indexes", asset_id + ".json"]))
        asset_list = asset_info["objects"]

        is_virtual = False
        if ("virtual" in asset_info):
            if (asset_info["virtual"] == True):
                is_virtual = True

        if not (progress_function == None):
            progress_function("Finding missing assets", 0)
        asset_dict = dict()
        if (is_virtual):
            assets_base_path = ["bin", "assets", "virtual", asset_id]
            if not self.Launcher.FileTools.path_exists(self.Launcher.FileTools.get_full_path(assets_base_path)):
                for asset_name in asset_list.keys():
                    asset_path_list = [asset_list[asset_name]["hash"][:2], asset_list[asset_name]["hash"]]
                    asset_dict[self.Launcher.NetworkTools.RESOURCES_URL + "/".join(asset_path_list)] = self.Launcher.FileTools.get_full_path(assets_base_path + asset_name.split("/"))
        else:
            for asset in asset_list.values():
                asset_path_list = [asset["hash"][:2], asset["hash"]]
                asset_absolute_path = self.Launcher.FileTools.get_full_path(["bin", "assets", "vanilla"] + asset_path_list)
                if not self.Launcher.FileTools.path_exists(asset_absolute_path):
                    asset_dict[self.Launcher.NetworkTools.RESOURCES_URL + "/".join(asset_path_list)] = asset_absolute_path

        asset_count = 0
        asset_total_count = len(asset_dict)
        for asset_url in asset_dict.keys():
            asset_url_object = self.Launcher.NetworkTools.get_url_object(asset_url)
            self.Launcher.FileTools.write_object(asset_dict[asset_url], asset_url_object)
            asset_count += 1
            if not (progress_function == None):
                progress_function("Downloading assets", asset_count/asset_total_count)

class AccountManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj
        self.GAME_USERNAME = "YAMCL"
        self.IS_OFFLINE = True
