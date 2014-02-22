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

from yamcl.globals import DataPath, URL

class AssetsManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

        self.BASE_PATH = DataPath("assets")

    def download_asset_index(self, asset_id):
        '''
        Downloads the JSON asset index specified by 'asset_id'
        '''
        asset_url_object = URL("indexes/" + asset_id + ".json", URL.DOWNLOAD).url_object()
        asset_index_path = str(self.BASE_PATH + DataPath("indexes/" + asset_id + ".json"))
        self.Launcher.FileTools.write_object(asset_index_path, asset_url_object)

    def download_missing_assets(self, asset_id, progress_function=None):
        '''
        Downloads assets specified in 'asset_id' that are not already downloaded
        '''
        asset_info = self.Launcher.FileTools.read_json(str(self.BASE_PATH + DataPath("indexes/" + asset_id + ".json")))
        asset_list = asset_info["objects"]

        is_virtual = False
        if ("virtual" in asset_info):
            if (asset_info["virtual"] == True):
                is_virtual = True

        if not (progress_function == None):
            progress_function("Finding missing assets", 0)
        asset_dict = dict()
        if (is_virtual):
            assets_base_path = self.BASE_PATH + DataPath("virtual/" + asset_id)
            if not assets_base_path.exists():
                for asset_name in asset_list.keys():
                    asset_url = URL([asset_list[asset_name]["hash"][:2], asset_list[asset_name]["hash"]], URL.RESOURCES)
                    asset_dict[asset_url] = str(assets_base_path + DataPath(asset_name))
        else:
            for asset in asset_list.values():
                asset_relative_path = [asset["hash"][:2], asset["hash"]]
                asset_url = URL(asset_relative_path, URL.RESOURCES)
                asset_path = self.BASE_PATH + DataPath(["objects"] + asset_relative_path)
                if not asset_path.exists():
                    asset_dict[asset_url] = str(asset_path)

        asset_count = 0
        asset_total_count = len(asset_dict)
        for asset_url in asset_dict.keys():
            asset_url_object = asset_url.url_object()
            self.Launcher.FileTools.write_object(asset_dict[asset_url], asset_url_object)
            asset_count += 1
            if not (progress_function == None):
                progress_function("Downloading assets", asset_count/asset_total_count)

    def get_paths(self, asset_id):
        '''
        Returns a dictionary containing the path to the index and directory for assets ID 'asset_id'
        '''
        asset_index_path = str(self.BASE_PATH + DataPath("indexes/" + asset_id + ".json"))
        asset_info = self.Launcher.FileTools.read_json(asset_index_path)

        asset_paths = dict()
        asset_paths["index"] = asset_index_path
        is_virtual = False
        if ("virtual" in asset_info):
            if (asset_info["virtual"] == True):
                asset_paths["directory"] = str(self.BASE_PATH + DataPath("virtual/" + asset_id))
                return asset_paths
        asset_paths["directory"] = str(self.BASE_PATH + DataPath("objects"))
        return asset_paths

class AccountManager:
    def __init__(self):
        self.GAME_USERNAME = "Player"
        self.IS_OFFLINE = True

    def set_game_username(self, new_username):
        '''
        Sets a new username 'new_username' only if in offline mode
        '''
        if (self.IS_OFFLINE):
            self.GAME_USERNAME = new_username

    def get_game_username(self):
        '''
        Gets the in-game username
        '''
        return self.GAME_USERNAME

    def is_offline(self):
        '''
        Returns boolean stating whether the launcher is logged in or not
        '''
        return self.IS_OFFLINE

class VersionsListManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

        self.versions_json = None

    def download_versions(self):
        '''
        Downloads the latest versions.json from the official servers
        '''
        tmp_file_object = str(URL("versions/versions.json", URL.DOWNLOAD))
        versions_path = str(DataPath("bin/versions.json"))
        self.Launcher.FileTools.write_object(versions_path, tmp_file_object)

        self.versions_json = None
        self.get_versions()

    def get_versions(self):
        '''
        Returns the object form of the versions.json file. If it is not loaded, it will be automatically loaded.
        '''
        if (self.versions_json is None):
            versions_path = str(DataPath("bin/versions.json"))
            self.versions_json = self.Launcher.FileTools.read_json(versions_path)
        return self.versions_json

    def version_exists(self, version_id):
        for current_version in self.version_json["versions"]:
            if current_version == version_id:
                return True
        return False

    def get_latest_release(self):
        pass

    def get_latest_snapshot(self):
        pass
