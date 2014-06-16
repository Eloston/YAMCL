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

class JSONTools:
    @staticmethod
    def read_json(raw_data):
        return json.JSONDecoder().decode(raw_data)

    @staticmethod
    def create_json(json_obj):
        return json.JSONEncoder(indent=2).encode(json_obj)

    @staticmethod
    def serialize_json(json_obj):
        return json.dumps(json_obj)

class FileTools:
    TEXT_ENCODING = "UTF-8"

    # General methods

    @staticmethod
    def write_string(file_path, file_string):
        '''
        Writes file in path 'file_path' with string 'file_string'. Will create directories as necessary
        '''
        FileTools.add_missing_dirs(file_path)
        with open(file_path, mode="w") as tmp_file_obj:
            tmp_file_obj.write(file_string)

    @staticmethod
    def write_object(file_path, file_object):
        '''
        Writes file in path 'file_path' with file object 'file_object'. Will create directories as necessary
        '''
        FileTools.add_missing_dirs(file_path)
        with open(file_path, mode="wb") as out_file:
            shutil.copyfileobj(file_object, out_file)
        file_object.close()

    # JSON methods

    @staticmethod
    def read_json(json_path):
        '''
        Returns a JSON object from file path 'json_path'
        '''
        with open(json_path, encoding=FileTools.TEXT_ENCODING) as tmp_file_obj:
            raw_data = tmp_file_obj.read()
        return JSONTools.read_json(raw_data)

    @staticmethod
    def write_json(json_path, json_obj):
        '''
        Writes JSON object 'json_obj' to path 'json_path'
        '''
        FileTools.add_missing_dirs(json_path)
        with open(json_path, mode="wb") as tmp_file_obj:
            tmp_file_obj.write(JSONTools.create_json(json_obj).encode(FileTools.TEXT_ENCODING))

    # jar file methods

    @staticmethod
    def get_jar_object(jar_path):
        '''
        Creates a jar object from jar file on path 'jar_path'
        '''
        return zipfile.ZipFile(jar_path)

    @staticmethod
    def extract_jar_files(jar_object, destination_dir, exclude_list=list()):
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

    @staticmethod
    def add_missing_dirs(file_path):
        '''
        Recursively adds the directories that are missing on file path 'file_path'
        '''
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

    @staticmethod
    def copy(source_path, destination_path):
        '''
        Copies file 'source_path' into directory or file 'destination_path'
        '''
        FileTools.add_missing_dirs(destination_path)
        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
        else:
            shutil.copy(source_path, destination_path)

    @staticmethod
    def delete_and_clean(path):
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

    @staticmethod
    def create_valid_name(name):
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

    @staticmethod
    def get_file_name(path):
        '''
        Wrapper around os.path.basename
        '''
        return os.path.basename(path)

    @staticmethod
    def rename(src, dst):
        '''
        Wrapper around os.rename
        '''
        os.rename(src, dst)

    @staticmethod
    def move(src, dst):
        '''
        Wrapper around shutil.move
        '''
        shutil.move(src, dst)

    @staticmethod
    def exists(file_path):
        '''
        Wrapper around os.path.exists
        '''
        return os.path.exists(file_path)

    @staticmethod
    def is_file(file_path):
        '''
        Wrapper around os.path.isfile
        '''
        return os.path.isfile(file_path)

    def is_dir(dir_path):
        '''
        Wrapper around os.path.isdir
        '''
        return os.path.isdir(dir_path)

    @staticmethod
    def dir_name(file_path):
        '''
        Wrapper around os.path.dirname
        '''
        return os.path.dirname(file_path)

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
                try:
                    JAVA_REGISTRY_PATH = "Software\\JavaSoft\\Java Runtime Environment"
                    current_java_version = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, JAVA_REGISTRY_PATH, access=winreg.KEY_READ | winreg.KEY_WOW64_64KEY), "CurrentVersion")[0]
                    java_binary_path = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, JAVA_REGISTRY_PATH + "\\" + current_java_version, access=winreg.KEY_READ | winreg.KEY_WOW64_64KEY), "JavaHome")[0]
                    java_command = java_binary_path + "\\bin\\java.exe"
                except FileNotFoundError:
                    java_command = str()
            else:
                java_command = "java"
        self.java_path = shutil.which(os.path.expanduser(os.path.expandvars(java_command)))
        # self.java_path will be none if file is not executable
        self.os_info["arch"] = None
        if not self.java_path == None:
            self.java_path = os.path.abspath(self.java_path)
            # Everything in this 'if' statement is an ugly Windows hack
            if current_platform == "windows":
                import subprocess
                arg_arch_check = dict()
                arg_arch_check["-d32"] = "32"
                arg_arch_check["-d64"] = "64"
                for current_argument in arg_arch_check.keys():
                    if not "Error: This Java instance does not support a " in subprocess.Popen([self.java_path, current_argument], stderr=subprocess.PIPE).communicate()[1].decode("UTF-8").splitlines()[0]:
                        self.os_info["arch"] = arg_arch_check[current_argument]

        self.os_info["family"] = current_platform
        if self.os_info["arch"] == None: # On Windows, this statement will be True if the hack fails
            self.os_info["arch"] = platform.architecture(self.java_path)[0][:2] # If path doesn't exist, it will return the architecture of the running Python interpreter. On Windows, it will always return the architecture of the current Python.

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

    def get_java_arch(self):
        '''
        Returns the Java architecture. "32" for 32-bit and "64" for 64-bit
        '''
        return self.os_info["arch"]
