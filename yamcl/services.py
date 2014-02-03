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

class BinaryManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

        self.versions_json = None
        self.index = self.Launcher.FileTools.read_json(self.Launcher.FileTools.get_full_path(["bin", "index.json"]))

    def download_versions(self):
        tmp_file_object = self.Launcher.NetworkTools.get_url_object(self.Launcher.NetworkTools.VERSIONS_JSON_URL)
        versions_path = self.Launcher.FileTools.get_full_path(["bin", "versions.json"])
        self.Launcher.FileTools.write_object(versions_path, tmp_file_object)

        self.get_versions()

    def get_versions(self):
        if (self.versions_json is None):
            versions_path = self.Launcher.FileTools.get_full_path(["bin", "versions.json"])
            self.versions_json = self.Launcher.FileTools.read_json(versions_path)
        return self.versions_json

    def flush_index(self):
        self.Launcher.FileTools.write_json(self.Launcher.FileTools.get_full_path(["bin", "index.json"]), self.index)

    def download_version_id(self, version_id):
        jar_path = self.Launcher.FileTools.get_full_path(["bin", "vanilla", version_id, version_id + ".jar"])
        json_path = self.Launcher.FileTools.get_full_path(["bin", "vanilla", version_id, version_id + ".json"])

        self.Launcher.FileTools.write_object(jar_path, self.Launcher.NetworkTools.get_url_object(self.Launcher.NetworkTools.DOWNLOAD_URL + "versions/" + version_id + "/" + version_id + ".jar"))
        self.Launcher.FileTools.write_object(json_path, self.Launcher.NetworkTools.get_url_object(self.Launcher.NetworkTools.DOWNLOAD_URL + "versions/" + version_id + "/" + version_id + ".json"))

        current_listing = dict()
        current_listing["type"] = "vanilla"
        current_listing["name"] = version_id
        current_listing["directory"] = version_id

        self.index.append(current_listing)

        self.flush_index()

class LibraryManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

        self.index = self.Launcher.FileTools.read_json(self.Launcher.FileTools.get_full_path(["lib", "index.json"]))

    def flush_index(self):
        self.Launcher.FileTools.write_json(self.Launcher.FileTools.get_full_path(["lib", "index.json"]), self.index)

    def create_vanilla_path(self, library_id):
        pass

class ProfileManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

class ProfileInstance:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

class AssetManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

class AccountManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj
