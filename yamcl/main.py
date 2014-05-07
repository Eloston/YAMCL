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

import yamcl.tools
import yamcl.binaries
import yamcl.libraries
import yamcl.managers
import yamcl.profiles
from yamcl.globals import DataPath

class Launcher:
    def __init__(self):
        self.COMPATIBLE_VERSION = 14
        self.PLATFORM_LIST = ["linux", "windows", "osx"]

        self.FileTools = yamcl.tools.FileTools()

    def startup(self, data_path=str(), java_command=str()):
        '''
        -Initializes all the classes.
        -"data_path" has path to YAMCL_data. If blank, set path to the current directory of this program.
        -Will setup YAMCL_data if necessary
        '''
        DataPath.set_data_path(data_path)
        if (self.check_data_integrity()):
            self.PlatformTools = yamcl.tools.PlatformTools(java_command)

            self.BinaryManager = yamcl.binaries.BinaryManager(self)
            self.LibraryManager = yamcl.libraries.LibraryManager(self)
            self.ProfileManager = yamcl.profiles.ProfileManager(self)
            self.AssetsManager = yamcl.managers.AssetsManager(self)
            self.AccountManager = yamcl.managers.AccountManager()
            self.VersionsListManager = yamcl.managers.VersionsListManager(self)

            return "SUCCESS"
        else:
            return "FAIL_DATACORRUPT"

    def create_skeleton_structure(self):
        '''
        Creates the skeleton structure for YAMCL data
        '''
        self.FileTools.write_json(str(DataPath("lib/index.json")), dict())
        self.FileTools.write_json(str(DataPath("bin/index.json")), list())
        self.FileTools.write_json(str(DataPath("profile/index.json")), dict())

    def check_data_integrity(self):
        '''
        Returns True if the current YAMCL data structural integrity is holding, False otherwise
        '''
        try:
            if (self.FileTools.get_root_data_path().is_directory()):
                if (DataPath("lib").is_directory() and DataPath("bin").is_directory() and DataPath("profile").is_directory()):
                    if (not DataPath("lib/index.json").is_directory() and not DataPath("bin/index.json").is_directory() and not DataPath("profile/index.json").is_directory()):
                        return True
        except FileNotFoundError:
            pass
        return False

    def shutdown(self):
        '''
        Launcher cleans itself up and exits
        '''
        self.AccountManager.shutdown()
