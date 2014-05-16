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

import urllib.request

class URL:
    protocol = "https://"
    # Base URLs
    DOWNLOAD = protocol + "s3.amazonaws.com/Minecraft.Download/"
    RESOURCES = protocol + "resources.download.minecraft.net/"
    LIBRARIES = protocol + "libraries.minecraft.net/" # Requires HTTPS protocol
    AUTH = protocol + "authserver.mojang.com/"

    def __init__(self, new_path, url_type=""):
        '''
        The path must be a relative path
        url_type is one of the URL prefixes defined in this class
        '''
        # None for url_prefix is allowed for purely relative URL paths, which are to be joined with other URLs.
        self.url_prefix = url_type
        if isinstance(new_path, list):
            self._relative_path = new_path
        elif isinstance(new_path, str):
            self._relative_path = new_path.split("/")

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
        return self.url_prefix + "/".join(self._relative_path)

    def __repr__(self):
        return "<YAMCL URL: " + self.__str__() + ">"

    def __add__(self, other_path):
        '''
        Adds the relative URL paths together, and returns a new URL object
        '''
        return URL(self._relative_path + other_path.get_relative_path())

    def __eq__(self, other_path):
        '''
        Checks to see if the URLs are the same
        '''
        return self._relative_path == other_path.get_relative_path()

    def __hash__(self):
        return str(self).__hash__()

    def get_relative_path(self):
        return self._relative_path
