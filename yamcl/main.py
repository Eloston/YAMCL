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

import sys
import shutil
import platform
import os.path
import pathlib

import yamcl.tools
import yamcl.binaries
import yamcl.libraries
import yamcl.managers
import yamcl.profiles
import yamcl.accounts

class Launcher:
    def __init__(self):
        self.COMPATIBLE_VERSION = 14
        self.PLATFORM_LIST = ["linux", "windows", "osx"]
        self.VERSION = "0.1"

    def startup(self, data_path=str(), java_command=str()):
        '''
        -Initializes all the classes.
        -"data_path" has path to YAMCL_data. If blank, set path to the current directory of this program.
        -Will setup YAMCL_data if necessary
        '''
        if len(data_path) == 0:
            self.ROOT_PATH = pathlib.Path(os.path.expanduser("~"), ".yamcl")
        else:
            self.ROOT_PATH = pathlib.Path(data_path).resolve()

        if (self.check_data_integrity()):
            self.PlatformTools = yamcl.tools.PlatformTools(java_command)

            self.BinaryManager = yamcl.binaries.BinaryManager(self)
            self.LibraryManager = yamcl.libraries.LibraryManager(self)
            self.ProfileManager = yamcl.profiles.ProfileManager(self)
            self.AssetsManager = yamcl.managers.AssetsManager(self)
            self.AccountManager = yamcl.accounts.AccountManager()
            self.VersionsListManager = yamcl.managers.VersionsListManager(self)

            return "SUCCESS"
        else:
            return "FAIL_DATACORRUPT"

    def create_skeleton_structure(self):
        '''
        Creates the skeleton structure for YAMCL data
        '''
        yamcl.tools.FileTools.write_json(str(self.ROOT_PATH.joinpath("lib/index.json")), dict())
        yamcl.tools.FileTools.write_json(str(self.ROOT_PATH.joinpath("bin/index.json")), list())
        yamcl.tools.FileTools.write_json(str(self.ROOT_PATH.joinpath("profile/index.json")), dict())

    def check_data_integrity(self):
        '''
        Returns True if the current YAMCL data structural integrity is holding, False otherwise
        '''
        try:
            if (self.ROOT_PATH.is_dir()):
                if self.ROOT_PATH.joinpath("lib").is_dir() and self.ROOT_PATH.joinpath("bin").is_dir() and self.ROOT_PATH.joinpath("profile").is_dir():
                    if not self.ROOT_PATH.joinpath("lib", "index.json").is_dir() and not self.ROOT_PATH.joinpath("bin", "index.json").is_dir() and not self.ROOT_PATH.joinpath("profile", "index.json").is_dir():
                        return True
        except FileNotFoundError:
            pass
        return False

    def shutdown(self):
        '''
        Launcher cleans itself up and exits
        '''
        self.AccountManager.shutdown()
