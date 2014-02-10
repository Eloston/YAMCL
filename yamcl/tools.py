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
import os
import shutil
import zipfile

class FileTools:
    def __init__(self, current_path):
        if (current_path == str()):
            self.data_path = os.path.join(os.path.expanduser("~"), ".yamcl")
        else:
            self.data_path = current_path

        # Constants
        self.TEXT_ENCODING = "UTF-8"

    # Relative path conversion methods

    def get_full_path(self, relative_path):
        '''
        Converts a relative path from the root of YAMCL's data directory to an absolute path
        Relative paths are a list containing strings of path elements (files and directories)
        '''
        absolute_path = self.data_path
        for path_element in relative_path:
            absolute_path = os.path.join(absolute_path, path_element)
        return absolute_path

    # YAMCL data specific

    def create_skeleton_structure(self):
        '''
        Creates the skeleton structure for YAMCL data
        '''
        self.write_json(self.get_full_path(["lib", "index.json"]), list())
        self.write_json(self.get_full_path(["bin", "index.json"]), list())
        self.write_json(self.get_full_path(["profile", "index.json"]), list())

    def check_data_integrity(self):
        '''
        Returns True if the current YAMCL data structural integrity is holding, False otherwise
        '''
        if (os.path.isdir(self.data_path)):
            if (os.path.isdir(self.get_full_path(["lib"])) and os.path.isdir(self.get_full_path(["bin"])) and os.path.isdir(self.get_full_path(["profile"]))):
                if (os.path.isfile(self.get_full_path(["lib", "index.json"])) and os.path.isfile(self.get_full_path(["bin", "index.json"])) and os.path.isfile(self.get_full_path(["profile", "index.json"]))):
                    return True
        return False

    # General methods

    def write_string(self, file_path, file_string):
        '''
        Writes file in path 'file_path' with string 'file_string'. Will create directories as necessary
        '''
        self.add_missing_dirs(file_path)
        with open(file_path, mode="w") as tmp_file_obj:
            tmp_file_obj.write(file_string)

    def write_object(self, file_path, file_object):
        '''
        Writes file in path 'file_path' with file object 'file_object'. Will create directories as necessary
        '''
        self.add_missing_dirs(file_path)
        with open(file_path, mode="wb") as out_file:
            shutil.copyfileobj(file_object, out_file)
        file_object.close()

    # JSON methods

    def read_json(self, json_path):
        '''
        Returns a JSON object from file path 'json_path'
        '''
        with open(json_path, encoding=self.TEXT_ENCODING) as tmp_file_obj:
            raw_data = tmp_file_obj.read()
        return json.JSONDecoder().decode(raw_data)

    def write_json(self, json_path, json_obj):
        '''
        Writes JSON object 'json_obj' to path 'json_path'
        '''
        self.add_missing_dirs(json_path)
        with open(json_path, mode="wb") as tmp_file_obj:
            tmp_file_obj.write(json.JSONEncoder(indent=2).encode(json_obj).encode(self.TEXT_ENCODING))

    # jar file methods

    def get_jar_object(self, jar_path):
        '''
        Creates a jar object from jar file on path 'jar_path'
        '''
        return zipfile.ZipFile(jar_path)

    def extract_jar_files(self, jar_object, destination_dir, exclude_list=list()):
        '''
        Extracts files from jar_object 'jar_object' to directory 'destination_dir', excluding files in 'exclude_list'
        '''
        jar_file_list = jar_object.namelist()
        if (len(exclude_list) > 0):
            good_list = list()
            for exclude in exclude_list:
                for member in jar_file_list:
                    if not member.startswith(exclude):
                        good_list.append(member)
            jar_file_list = good_list
        jar_object.extractall(destination_dir, jar_file_list)

    # Other methods

    def add_missing_dirs(self, file_path):
        '''
        Recursively adds the directories that are missing on file path 'file_path'
        '''
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def copy_files(self, source_path, destination_path):
        '''
        Copies file 'source_path' into directory or file 'destination_path'
        '''
        shutil.copy(source_path, destination_path)

    def path_exists(self, path):
        '''
        Checks to see if path exists (whether a directory or file)
        '''
        return os.path.exists(path)

    def delete_file(self, path):
        '''
        Deletes a file
        '''
        os.remove(path)

    def delete_and_clean(self, path):
        '''
        Deletes path 'path' (will recursively delete directory)
        Directories that have become empty will be removed starting from the file's directory.
        '''
        # TODO: use os.removedirs(path) to delete empty directories
        # TODO: use shutil.rmtree() to delete jar or natives, but not clear empty directories
        pass

class NetworkTools:
    def __init__(self):
        protocol = "https://"

        # Base URLs
        self.DOWNLOAD_URL = protocol + "s3.amazonaws.com/Minecraft.Download/"
        self.RESOURCES_URL = protocol + "resources.download.minecraft.net/"
        self.LIBRARIES_URL = protocol + "libraries.minecraft.net/" # Requires HTTPS protocol

        # Specific URLs
        self.VERSIONS_JSON_URL = self.DOWNLOAD_URL + "versions/versions.json"
        self.INDEXES_URL = self.DOWNLOAD_URL + "indexes/"

    def get_url_object(self, url):
        '''
        Returns a URL object that supports the file IO interface
        '''
        return urllib.request.urlopen(url)
