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

import yamcl.tools
import yamcl.services

class Launcher:
    def __init__(self):
        self.COMPATIBLE_VERSION = 13

    def startup(self, data_path="", platform_override="", java_command="", use_https=True):
        '''
        -Initializes all the classes.
        -Reads main configuration file.
        -"data_path" has path to YAMCL_data. If blank, set path to the current directory of this program.
        -Will setup YAMCL_data if necessary
        -Get OS family and architecture
        '''
        self.FileTools = yamcl.tools.FileTools(data_path)
        self.NetworkTools = yamcl.tools.NetworkTools(use_https)

        self.BinaryManager = yamcl.services.BinaryManager(self)
        self.LibraryManager = yamcl.services.LibraryManager(self)
        self.ProfileManager = yamcl.services.ProfileManager(self)
        self.AssetManager = yamcl.services.AssetManager(self)
        self.AccountManager = yamcl.services.AccountManager(self)

    def shutdown(self):
        '''
        Launcher cleans itself up and exits
        '''
        pass

    def get_os_family(self):
        '''
        Returns the current OS family name. Either "windows", "osx", or "linux". Will return "linux" if it is not osx or windows
        '''
        if (sys.platform == "win32" or sys.platform == "cygwin"):
            return "windows"
        else if (sys.platform == "darwin"):
            return "osx"
        else:
            return "linux"

    def get_os_arch(self):
        '''
        Returns the architecture the OS is built for. "32" for 32-bit and "64" for 64-bit
        '''
        pass
