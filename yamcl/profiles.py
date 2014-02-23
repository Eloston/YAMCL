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

import subprocess
import os

from yamcl.globals import DataPath

class ProfileManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj
        self.BASE_PATH = DataPath("profile")

        self.index = self.Launcher.FileTools.read_json(str(self.BASE_PATH + DataPath("index.json")))
        self.profile_instances = dict()

    def flush_index(self):
        '''
        Writes current profile index in memory to the YAMCL data directory
        '''
        self.Launcher.FileTools.write_json(str(self.BASE_PATH + DataPath("index.json")), self.index)

    def get_java_path(self):
        '''
        Returns the path to the java binary
        '''
        return self.java_path

    def add_profile(self, profile_name):
        '''
        Creates a new profile with name 'profile_name'
        '''
        if not profile_name in self.index:
            self.index[profile_name] = dict()
            self.index[profile_name]["directory"] = [profile_name] # TODO: Convert to filesystem-friendly name
            profile_metadata = dict()
            profile_metadata["notes"] = str()
            profile_metadata["vanillaversions"] = list()
            profile_metadata["customversions"] = list()
            self.Launcher.FileTools.write_json(str(self.BASE_PATH + DataPath(profile_name + "/yamcl_metadata.json")), profile_metadata)
            self.flush_index()

    def delete_profile(self, profile_name):
        '''
        Deletes profile 'profile_name'
        '''
        if not profile_name in self.index:
            raise Exception("Profile " + str(profile_name) + " does not exist") # TODO: More appropriate exception
        self.Launcher.FileTools.delete_and_clean(str(self.BASE_PATH + DataPath(self.index[profile_name]["directory"])))
        del self.index[profile_name]
        self.flush_index()

    def get_profile_instance(self, profile_name):
        '''
        Returns a ProfileInstance of profile 'profile_name'
        '''
        if not profile_name in self.index:
            raise Exception("Profile " + str(profile_name) + " does not exist") # TODO: More appropriate exception
        if profile_name in self.profile_instances:
            return self.profile_instances[profile_name]
        else:
            profile_directory = self.BASE_PATH + DataPath(self.index[profile_name]["directory"])
            new_profile_instance = ProfileInstance(self.Launcher, profile_name, profile_directory)
            self.profile_instances[profile_name] = new_profile_instance
            return new_profile_instance

    def delete_profile_instance(self, profile_name):
        '''
        Closes ProfileInstance 'profile_name'
        '''
        if profile_name in self.profile_instances:
            self.profile_instances[profile_name].shutdown()
            del self.profile_instances[profile_name]

    def shutdown(self):
        '''
        Closes all ProfileInstances
        '''
        pass

class ProfileInstance:
    def __init__(self, launcher_obj, name, profile_path):
        self.Launcher = launcher_obj

        self.profile_name = name
        self.data_path = profile_path
        self.metadata = self.Launcher.FileTools.read_json(str(self.data_path + DataPath("yamcl_metadata.json")))
        self.game_process = None

    def flush_metadata(self):
        '''
        Writes current library index in memory to the YAMCL data directory
        '''
        self.Launcher.FileTools.write_json(str(self.data_path + DataPath("yamcl_metadata.json")), self.metadata)

    def get_notes(self):
        '''
        Returns a string containing the notes
        '''
        return self.metadata["notes"]

    def set_notes(self, new_notes):
        '''
        Updates notes for this profile
        '''
        self.metadata["notes"] = new_notes
        self.flush_metadata()

    def add_version(self, version_id, version_type):
        '''
        Adds a version to the metadata
        '''
        if not version_id in self.metadata[version_type + "versions"]:
            self.metadata[version_type + "versions"].append(version_id)
        self.flush_metadata()

    def delete_version(self, version_id, version_type):
        '''
        Removes a version from the metadata
        '''
        if version_id in self.metadata[version_type + "versions"]:
            self.metadata.remove(version_type + "versions")
        self.flush_metadata()

    def check_game_running(self):
        '''
        Checks to see if the game is still running
        '''
        if not (self.game_process == None):
            if self.game_process.poll() == None:
                return True
        return False

    def launch_version(self, version_id, version_type):
        '''
        Launches the game 'version_id' of type 'version_type'
        '''
        game_binary_parser = self.Launcher.BinaryManager.get_binary_parser(version_id, version_type)
        game_arguments = dict()
        game_arguments["profile_name"] = self.profile_name
        game_arguments["version_name"] = game_binary_parser.get_id()
        game_arguments["game_directory"] = str(self.data_path)
        game_arguments["game_assets"] = self.Launcher.AssetsManager.get_paths(game_binary_parser.get_assets_id())["directory"]
        game_arguments["assets_root"] = str(self.Launcher.AssetsManager.BASE_PATH)
        game_arguments["assets_index_name"] = game_binary_parser.get_assets_id()
        if self.Launcher.AccountManager.is_offline():
            game_arguments["auth_username"] = self.Launcher.AccountManager.get_game_username()
            game_arguments["auth_player_name"] = game_arguments["auth_username"]
            game_arguments["auth_uuid"] = "00000000-0000-0000-0000-000000000000"
            game_arguments["auth_session"] = "-"
            game_arguments["auth_access_token"] = "0"
            game_arguments["user_type"] = "legacy"
            game_arguments["user_properties"] = str(dict())
        else:
            pass # TODO: Implement authentication

        version_paths = self.Launcher.BinaryManager.get_paths(version_id, version_type)

        launch_arguments = list()
        if self.Launcher.PlatformTools.get_java_path() == None:
            raise Exception("Could not find a Java binary to launch") # TODO: more appropriate exception
        launch_arguments.append(self.Launcher.PlatformTools.get_java_path())
        launch_arguments.append("-Xmx1G") # TODO: More customizeable arguments
        libraries_dict = self.Launcher.LibraryManager.get_platform_paths(game_binary_parser.get_library_parsers())
        launch_arguments.append("-Djava.library.path=" + '"' + ":".join(libraries_dict["natives"]) + '"')
        launch_arguments.append("-cp " + ":".join(libraries_dict["jars"] + [version_paths["jar"]]))
        launch_arguments.append(game_binary_parser.get_launch_class())
        launch_arguments.append(game_binary_parser.get_arguments(game_arguments))
        os.chdir(game_arguments["game_directory"]) # Needed for logs to be created in the proper directory
        self.game_process = subprocess.Popen(" ".join(launch_arguments), shell=True)

    def shutdown(self):
        '''
        Shuts down Minecraft if running
        '''
        if not (self.game_process == None):
            self.game_process.terminate()
