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

import os.path
import urllib.request

class DataPath:
    @staticmethod
    def set_data_path(current_path):
        '''
        Should only be set once by FileTools
        '''
        if (current_path == str()):
            DataPath.data_path = os.path.join(os.path.expanduser("~"), ".yamcl")
        else:
            DataPath.data_path = current_path

    @staticmethod
    def _get_data_path():
        return DataPath.data_path

    def __init__(self, new_path):
        '''
        The path must be a relative path
        '''
        if isinstance(new_path, list):
            self.relative_path = new_path
        elif isinstance(new_path, str):
            new_path = os.path.normpath(new_path)
            self.relative_path = list()
            if os.path.isabs(new_path):
                tmp_relative = os.path.relpath(new_path, start=DataPath.data_path)
            else:
                tmp_relative = new_path
            while True:
                tmp_split = os.path.split(tmp_relative)
                self.relative_path = [tmp_split[1]] + self.relative_path
                if tmp_split[0] == str():
                    break
                else:
                    tmp_relative = tmp_split[0]

    def __str__(self):
        '''
        Returns an absolute path of the current path object
        '''
        return os.path.join(self._get_data_path(), *self.relative_path)

    def __repr__(self):
        return "<YAMCL DataPath: " + self.__str__() + ">"

    def __eq__(self, other_path):
        '''
        Checks to see if the paths are the same
        '''
        return self.relative_path == other_path.relative_path

    def __add__(self, other_path):
        '''
        Adds the relative paths together, and returns a new path object
        '''
        return DataPath(self.relative_path + other_path.relative_path)

    def __sub__(self, other_path):
        '''
        Returns a new path object that has a path relative to other_path
        '''
        return DataPath(os.path.relpath(str(self), start=str(other_path)))

    def __hash__(self):
        return str(self).__hash__()

    def is_directory(self):
        '''
        Returns True if path is a directory, False otherwise
        '''
        absolute_path = str(self)
        if os.path.exists(absolute_path):
            return os.path.isdir(absolute_path)
        else:
            raise FileNotFoundError("Cannot find file: " + absolute_path)

    def exists(self):
        '''
        Returns True if path exists, False otherwise
        '''
        return os.path.exists(str(self))

    def directory_path(self):
        '''
        Returns the DataPath of the containing directory.
        '''
        return DataPath(self.relative_path[:-1])

    def file_name(self):
        '''
        Returns the last path element
        '''
        return self.relative_path[-1]

    def get_relative_path(self):
        '''
        Returns the relative path list
        '''
        return self.relative_path

class URL:
    protocol = "https://"
    # Base URLs
    DOWNLOAD = protocol + "s3.amazonaws.com/Minecraft.Download/"
    RESOURCES = protocol + "resources.download.minecraft.net/"
    LIBRARIES = protocol + "libraries.minecraft.net/" # Requires HTTPS protocol

    def __init__(self, new_path, url_type=None):
        '''
        The path must be a relative path
        url_type is one of the URL prefixes defined in this class
        '''
        # None for url_prefix is allowed for purely relative URL paths, which are to be joined with other URLs.
        self.url_prefix = url_type
        if isinstance(new_path, list):
            self.relative_path = new_path
        elif isinstance(new_path, str):
            self.relative_path = new_path.split("/")

    def url_object(self):
        '''
        Returns a URL object
        '''
        return urllib.request.urlopen(self.__str__())

    def __str__(self):
        '''
        Converts a relative path in a URL to an absolute path
        '''
        if self.url_prefix == None:
            raise TypeError("No URL prefix specified")
        return self.url_prefix + "/".join(self.relative_path)

    def __repr__(self):
        return "<YAMCL URL: " + self.__str__() + ">"

    def __add__(self, other_path):
        '''
        Adds the relative URL paths together, and returns a new URL object
        '''
        return URL(self.relative_path + other_path.relative_path)

    def __eq__(self, other_path):
        '''
        Checks to see if the URLs are the same
        '''
        return self.relative_path == other_path.relative_path

    def __hash__(self):
        return str(self).__hash__()
