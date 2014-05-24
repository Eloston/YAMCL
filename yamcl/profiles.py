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

from yamcl.tools import FileTools

class ProfileManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj
        self.BASE_PATH = self.Launcher.ROOT_PATH.joinpath("profile")

        self.index = FileTools.read_json(str(self.BASE_PATH.joinpath("index.json")))
        self.profile_instances = dict()

    def _flush_index(self):
        '''
        Writes current profile index in memory to the YAMCL data directory
        '''
        FileTools.write_json(str(self.BASE_PATH.joinpath("index.json")), self.index)

    def get_profile_list(self):
        '''
        Returns a list of all profiles
        '''
        return list(self.index.keys())

    def new(self, profile_name):
        '''
        Creates a new profile with name 'profile_name'
        '''
        if not profile_name in self.index:
            self.index[profile_name] = dict()
            self.index[profile_name]["directory"] = [FileTools.create_valid_name(profile_name)]
            profile_metadata = dict()
            profile_metadata["notes"] = str()
            profile_metadata["lastversion"] = dict()
            profile_metadata["lastversion"]["id"] = ""
            profile_metadata["lastversion"]["type"] = ""
            FileTools.write_json(str(self.BASE_PATH.joinpath(profile_name + "/yamcl_metadata.json")), profile_metadata)
            self._flush_index()

    def delete(self, profile_name):
        '''
        Deletes profile 'profile_name'
        '''
        if not profile_name in self.index:
            raise Exception("Profile " + str(profile_name) + " does not exist") # TODO: More appropriate exception
        FileTools.delete_and_clean(str(self.BASE_PATH.joinpath(*self.index[profile_name]["directory"])))
        del self.index[profile_name]
        self._flush_index()

    def rename(self, current_profile_name, new_profile_name):
        '''
        Renames a profile 'current_profile_name' to a new name 'new_profile_name'
        '''
        if not current_profile_name in self.index:
            raise Exception("Cannot rename: " + current_profile_name + " does not exist")
        if new_profile_name in self.index:
            raise Exception("Cannot rename: " + new_profile_name + " already exists")
        FileTools.rename(str(self.BASE_PATH.joinpath(*self.index[current_profile_name]["directory"])), str(self.BASE_PATH.joinpath(FileTools.create_valid_name(new_profile_name))))
        del self.index[current_profile_name]
        self.index[new_profile_name] = dict()
        self.index[new_profile_name]["directory"] = [FileTools.create_valid_name(new_profile_name)]
        self._flush_index()

    def get_profile_instance(self, profile_name):
        '''
        Returns a ProfileInstance of profile 'profile_name'
        '''
        if not profile_name in self.index:
            raise Exception("Profile " + str(profile_name) + " does not exist") # TODO: More appropriate exception
        if profile_name in self.profile_instances:
            return self.profile_instances[profile_name]
        else:
            profile_directory = self.BASE_PATH.joinpath(*self.index[profile_name]["directory"])
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
        self.metadata = FileTools.read_json(str(self.data_path.joinpath("yamcl_metadata.json")))
        self.game_process = None

    def flush_metadata(self):
        '''
        Writes current library index in memory to the YAMCL data directory
        '''
        FileTools.write_json(str(self.data_path.joinpath("yamcl_metadata.json")), self.metadata)

    def get_name(self):
        '''
        Returns the profile name
        '''
        return self.profile_name

    def get_path(self):
        return self.data_path

    def get_last_version(self):
        '''
        Returns the last version launched
        '''
        return self.metadata["lastversion"]

    def set_last_version(self, version_id, version_type):
        '''
        Sets the last version launched
        '''
        self.metadata["lastversion"]["id"] = version_id
        self.metadata["lastversion"]["type"] = version_type
        self.flush_metadata()

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
        game_arguments["game_assets"] = str(self.Launcher.AssetsManager.get_paths(game_binary_parser.get_assets_id())["directory"])
        game_arguments["assets_root"] = str(self.Launcher.AssetsManager.BASE_PATH)
        game_arguments["assets_index_name"] = game_binary_parser.get_assets_id()

        game_arguments["auth_username"] = self.Launcher.AccountManager.get_account().get_account_username()
        game_arguments["auth_player_name"] = self.Launcher.AccountManager.get_account().get_game_username()
        game_arguments["auth_uuid"] = self.Launcher.AccountManager.get_account().get_uuid()
        game_arguments["auth_session"] = self.Launcher.AccountManager.get_account().get_session()
        game_arguments["auth_access_token"] = self.Launcher.AccountManager.get_account().get_access_token()
        game_arguments["user_type"] = self.Launcher.AccountManager.get_account().get_user_type()
        game_arguments["user_properties"] = self.Launcher.AccountManager.get_account().get_user_properties()

        version_paths = self.Launcher.BinaryManager.get_paths(version_id, version_type)

        launch_arguments = list()
        if self.Launcher.PlatformTools.get_java_path() == None:
            raise Exception("Could not find a Java binary to launch") # TODO: more appropriate exception
        launch_arguments.append('"' + self.Launcher.PlatformTools.get_java_path() + '"')
        launch_arguments.append("-Xmx1G") # TODO: More customizeable arguments
        libraries_dict = self.Launcher.LibraryManager.get_platform_paths(game_binary_parser.get_library_parsers())
        launch_arguments.append("-Djava.library.path=" + '"' + self.Launcher.PlatformTools.JAVA_PATH_DELIM.join(libraries_dict["natives"]) + '"')
        launch_arguments.append("-cp " + self.Launcher.PlatformTools.JAVA_PATH_DELIM.join(libraries_dict["jars"] + [version_paths["jar"]]))
        launch_arguments.append(game_binary_parser.get_launch_class())
        launch_arguments.append(game_binary_parser.get_arguments(game_arguments))
        os.chdir(game_arguments["game_directory"]) # Needed for logs to be created in the proper directory
        self.game_process = subprocess.Popen(" ".join(launch_arguments), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    def get_output_object(self):
        if self.check_game_running():
            return self.game_process.stdout
        return None

    def kill_game(self):
        '''
        Shuts down Minecraft if running
        '''
        if not (self.game_process == None):
            self.game_process.terminate()

    def shutdown(self):
        # In the future, maybe an option will specify to kill Minecraft when shutting down a profile instance?
        pass
