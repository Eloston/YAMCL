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
import yamcl.services

class Launcher:
    def __init__(self, data_path=""):
        self.COMPATIBLE_VERSION = 13
        self.PLATFORM_LIST = ["linux", "windows", "osx"]
        # Necessary for checking 
        self.FileTools = yamcl.tools.FileTools(data_path)

    def startup(self, platform_override="", java_command=""):
        '''
        -Initializes all the classes.
        -Reads main configuration file.
        -"data_path" has path to YAMCL_data. If blank, set path to the current directory of this program.
        -Will setup YAMCL_data if necessary
        -Get OS family and architecture
        '''
        # Instantiate components

        if (self.FileTools.check_data_integrity()):
            self.NetworkTools = yamcl.tools.NetworkTools()
            
            self.BinaryManager = yamcl.services.BinaryManager(self)
            self.LibraryManager = yamcl.services.LibraryManager(self)
            self.ProfileManager = yamcl.services.ProfileManager(self, java_command)
            self.AssetManager = yamcl.services.AssetManager(self)
            self.AccountManager = yamcl.services.AccountManager(self)

            # Setting OS information
            self.os_info = dict()
            if (sys.platform == "win32" or sys.platform == "cygwin"):
                current_platform = "windows"
            elif (sys.platform == "darwin"):
                current_platform = "osx"
            else:
                # Assuming it is linux, otherwise the user wouldn't be playing Minecraft to begin with
                current_platform = "linux"
            self.os_info["family"] = current_platform
            self.os_info["arch"] = platform.architecture(shutil.which(self.ProfileManager.java_path))[0][:2]

            return "SUCCESS"
        else:
            return "FAIL_DATACORRUPT"

    def shutdown(self):
        '''
        Launcher cleans itself up and exits
        '''
        pass

    def get_os_family(self):
        '''
        Returns the current OS family name. Either "windows", "osx", or "linux". Will return "linux" if it is not osx or windows
        '''
        return self.os_info["family"]

    def get_os_arch(self):
        '''
        Returns the architecture the OS is built for. "32" for 32-bit and "64" for 64-bit
        Uses the Java binary for determining the architecture
        '''
        return self.os_info["arch"]
