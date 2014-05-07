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
import os.path
import os
import shutil
import zipfile
import platform
import sys
import errno

from yamcl.globals import DataPath

class FileTools:
    def __init__(self):
        # Constants
        self.TEXT_ENCODING = "UTF-8"

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

    def get_root_data_path(self):
        return DataPath(list())

    def add_missing_dirs(self, file_path):
        '''
        Recursively adds the directories that are missing on file path 'file_path'
        '''
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    def copy(self, source_path, destination_path):
        '''
        Copies file 'source_path' into directory or file 'destination_path'
        '''
        self.add_missing_dirs(destination_path)
        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
        else:
            shutil.copy(source_path, destination_path)

    def delete_and_clean(self, path):
        '''
        Deletes path 'path' (will recursively delete directory)
        Directories that have become empty will be removed starting from the file's directory.
        '''
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        try:
            os.removedirs(os.path.dirname(path))
        except OSError as current_exception:
            if not current_exception.errno == errno.ENOTEMPTY:
                raise current_exception

    def create_valid_name(self, name):
        '''
        Creates a filesystem-friendly name
        '''
        new_name = ""
        for i in name:
            if (i.isalnum() or i in "_-.()[]{}"):
                new_name += i
            else:
                new_name += "_"
        return new_name

    def get_file_name(self, path):
        '''
        Wrapper around os.path.basename
        '''
        return os.path.basename(path)

    def rename(self, src, dst):
        '''
        Wrapper around os.rename
        '''
        os.rename(src, dst)

    def move(self, src, dst):
        '''
        Wrapper around shutil.move
        '''
        shutil.move(src, dst)

class PlatformTools:
    def __init__(self, java_command):
        self.os_info = dict()
        self.JAVA_PATH_DELIM = ":"
        if (sys.platform == "win32" or sys.platform == "cygwin"):
            current_platform = "windows"
            self.JAVA_PATH_DELIM = ";" # Every platform except Windows uses colon
        elif (sys.platform == "darwin"):
            current_platform = "osx"
        else:
            # Assuming it is linux, otherwise the user wouldn't be playing Minecraft to begin with
            current_platform = "linux"

        if (java_command == str()):
            if current_platform == "windows":
                import winreg
                JAVA_REGISTRY_PATH = "Software\\JavaSoft\\Java Runtime Environment"
                current_java_version = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, JAVA_REGISTRY_PATH), "CurrentVersion")[0]
                java_binary_path = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, JAVA_REGISTRY_PATH + "\\" + current_java_version), "JavaHome")[0]
                java_command = java_binary_path + "\\bin\\java.exe"
            else:
                java_command = "java"
        self.java_path = shutil.which(os.path.expanduser(os.path.expandvars(java_command)))
        # self.java_path will be none if file is not executable
        if not self.java_path == None:
            self.java_path = os.path.abspath(self.java_path)

        self.os_info["family"] = current_platform
        self.os_info["arch"] = platform.architecture(self.java_path)[0][:2]

    def get_java_path(self):
        '''
        Returns the path to the java binary
        '''
        return self.java_path

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
