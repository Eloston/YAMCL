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

import pathlib

from yamcl.tools import FileTools
from yamcl.globals import URL

class AssetsManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

        self.BASE_PATH = self.Launcher.ROOT_PATH.joinpath("assets")

    def download_index(self, asset_id):
        '''
        Downloads the JSON asset index specified by 'asset_id'
        '''
        asset_url_object = URL("indexes/" + asset_id + ".json", URL.DOWNLOAD).url_object()
        asset_index_path = str(self.BASE_PATH.joinpath("indexes/" + asset_id + ".json"))
        FileTools.write_object(asset_index_path, asset_url_object)

    def _is_virtual(self, asset_info):
        if ("virtual" in asset_info):
            return asset_info["virtual"] == True
        return False

    def download_missing(self, asset_id, progress_function=None):
        '''
        Downloads assets specified in 'asset_id' that are not already downloaded
        '''
        asset_info = FileTools.read_json(str(self.get_paths(asset_id)["index"]))
        asset_list = asset_info["objects"]

        if not (progress_function == None):
            progress_function("Finding missing assets", 0)
        asset_dict = dict()
        if (self._is_virtual(asset_info)):
            assets_base_path = self.BASE_PATH.joinpath("virtual/" + asset_id)
            if not assets_base_path.exists():
                for asset_name in asset_list.keys():
                    asset_url = URL([asset_list[asset_name]["hash"][:2], asset_list[asset_name]["hash"]], URL.RESOURCES)
                    asset_dict[asset_url] = str(assets_base_path.joinpath(asset_name))
        else:
            for asset in asset_list.values():
                asset_relative_path = [asset["hash"][:2], asset["hash"]]
                asset_url = URL(asset_relative_path, URL.RESOURCES)
                asset_path = self.BASE_PATH.joinpath(*(["objects"] + asset_relative_path))
                if not asset_path.exists():
                    asset_dict[asset_url] = str(asset_path)

        asset_count = 0
        asset_total_count = len(asset_dict)
        for asset_url in asset_dict.keys():
            asset_url_object = asset_url.url_object()
            FileTools.write_object(asset_dict[asset_url], asset_url_object)
            asset_count += 1
            if not (progress_function == None):
                progress_function("Downloading assets", asset_count/asset_total_count)

    def get_paths(self, asset_id):
        '''
        Returns a dictionary containing the path to the index and directory for assets ID 'asset_id'
        '''
        asset_index_path = self.BASE_PATH.joinpath("indexes/" + asset_id + ".json")
        if not asset_index_path.exists():
            raise Exception("Assets ID " + asset_id + " does not exist")

        asset_paths = dict()
        asset_paths["index"] = asset_index_path
        if self._is_virtual(FileTools.read_json(str(asset_index_path))):
            asset_paths["directory"] = str(self.BASE_PATH.joinpath("virtual/" + asset_id))
            return asset_paths
        asset_paths["directory"] = self.BASE_PATH.joinpath("objects")
        return asset_paths

    def _get_indexes(self):
        index_list = list()
        for index_path in self.BASE_PATH.joinpath("indexes").iterdir():
            index_list.append(index_path.stem)
        return index_list

    def _remove_unused_objects(self, asset_id_list):
        '''
        Removes assets from the 'objects' folder that are not present in the indexes 'asset_id_list'
        This does not include virtual assets
        '''
        used_hash_list = list()
        for asset_id in asset_id_list:
            current_assets = FileTools.read_json(str(self.get_paths(asset_id)["index"]))["objects"]
            for resource in current_assets.keys():
                current_hash = current_assets[resource]["hash"]
                if not current_hash in used_hash_list:
                    used_hash_list.append(current_hash)
        for prefix_hash_dir in self.BASE_PATH.joinpath("objects").iterdir():
            for hash_file in prefix_hash_dir.iterdir():
                if not hash_file.name in used_hash_list:
                    FileTools.delete_and_clean(str(hash_file))

    def delete(self, asset_id):
        '''
        Deletes assets 'asset_id'
        '''
        asset_paths = self.get_paths(asset_id)

        if self._is_virtual(FileTools.read_json(str(asset_paths["index"]))):
            FileTools.delete_and_clean(str(asset_paths["directory"]))
            FileTools.delete_and_clean(str(asset_paths["index"]))
        else:
            FileTools.delete_and_clean(str(asset_paths["index"]))
            self._remove_unused_objects(self._get_indexes())

    def get_unused(self, binary_parser_list):
        '''
        Returns a list of unused asset ids in binary_parser_list
        '''
        unused_assets_list = list()
        for existing_id in self._get_indexes():
            asset_used = False
            for binary_parser in binary_parser_list:
                if binary_parser.get_assets_id() == existing_id:
                    asset_used = True
                    break
            if not asset_used:
                unused_assets_list.append(existing_id)
        return unused_assets_list

class VersionsListManager:
    def __init__(self, launcher_obj):
        self.Launcher = launcher_obj

        self.BASE_PATH = self.Launcher.ROOT_PATH.joinpath("bin/versions.json")
        if self.BASE_PATH.exists():
            versions_path = str(self.BASE_PATH)
            self.versions_json = FileTools.read_json(versions_path)
        else:
            self.versions_json = None

    def download_versions(self):
        '''
        Downloads the latest versions.json from the official servers
        '''
        tmp_file_object = URL("versions/versions.json", URL.DOWNLOAD).url_object()
        versions_path = str(self.BASE_PATH)
        FileTools.write_object(versions_path, tmp_file_object)

        self.versions_json = FileTools.read_json(versions_path)

    def get_versions(self):
        '''
        Returns the object form of the versions.json file
        '''
        return self.versions_json

    def version_exists(self, version_id):
        for current_version in self.versions_json["versions"]:
            if current_version["id"] == version_id:
                return True
        return False

    def get_latest_release(self):
        return self.versions_json["latest"]["release"]

    def get_latest_snapshot(self):
        return self.versions_json["latest"]["snapshot"]
