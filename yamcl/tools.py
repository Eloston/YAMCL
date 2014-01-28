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

import json
import urllib.request
import os.path
import shutil

class FileTools:
    def __init__(self, current_path):
        if (current_path == str()):
            # TODO: Get APPDATA on Windows, HOME on Linux, ? on OSX
            pass
        else:
            self.data_path = current_path

    def check_data_integrity(self):
        '''
        Returns True if the current YAMCL data structural data is holding, False otherwise
        '''
        raise NotImplementedError()

    def write_file(self, file_path, file_data):
        '''
        Writes file in path 'file_path' with data 'file_data'. Will create directories as necessary
        '''
        raise NotImplementedError()

    def write_json(self, json_path, json_obj):
        '''
        Writes JSON object 'json_obj' to path 'json_path'
        '''
        raise NotImplementedError()

class NetworkTools:
    def __init__(self, use_https):
        if (use_https):
            protocol = "https://"
        else:
            protocol = "http://"

        # Base URLs
        self.DOWNLOAD_URL = protocol + "s3.amazonaws.com/Minecraft.Download/"
        self.RESOURCES_URL = protocol + "resources.download.minecraft.net/"
        self.LIBRARIES_URL = protocol + "libraries.minecraft.net/"        

        # Specific URLs
        self.VERSIONS_JSON_URL = self.DOWNLOAD_URL + "versions/versions.json"
        self.INDEXES_URL = self.DOWNLOAD_URL + "indexes/"
