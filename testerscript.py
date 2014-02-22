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

# Script to test YAMCL functionality

def status_function(status, progress_percentage):
    print(status + ": " + str(round(progress_percentage*100, 2)) + "%")

import yamcl.main

test_launcher = yamcl.main.Launcher()
print(test_launcher.startup(download_specific_libraries=True))
#test_launcher.create_skeleton_structure()
print("OS Family: " + test_launcher.PlatformTools.get_os_family() + "\nOS Arch: " + test_launcher.PlatformTools.get_os_arch())

# Download a Minecraft
#test_launcher.BinaryManager.download_official("1.7.4")
#test_launcher.BinaryManager.download_official("1.5.2")

# BinaryParser and LibraryParser testing

#print()
#print("BinaryParser")
#test_parser = test_launcher.BinaryManager.get_binary_parser("1.7.4", "vanilla")
test_parser = test_launcher.BinaryManager.get_binary_parser("1.5.2", "vanilla")
#print("Compatible with launcher:", test_parser.is_compatible())
#print("ID:", test_parser.get_id())

#print()
#print("LibraryParser")
#library_parsers = test_parser.get_library_parsers()
#for current_parser in library_parsers:
#    print(current_parser.get_id(), "system supported:", current_parser.current_system_supported())

#print("Current system natives extension:", library_parsers[-4].get_current_system_natives_extension())
#print()
#test_launcher.LibraryManager.download_missing_libraries(library_parsers, status_function)
#print(test_launcher.LibraryManager.get_library_paths(library_parsers))

# AssetsManager testing
test_launcher.AssetsManager.download_asset_index(test_parser.get_assets_id())
test_launcher.AssetsManager.download_missing_assets(test_parser.get_assets_id(), status_function)

#test_launcher.ProfileManager.add_profile("Old_1.5.2")

#test_launcher.ProfileManager.get_profile_instance("Latest").launch_version("1.7.4", "vanilla")

# Old code
'''
test_launcher = yamcl.main.Launcher()
test_launcher.startup()
print("Data Integrity Check Holding: " + str(test_launcher.FileTools.check_data_integrity()))
print("OS Family: " + test_launcher.get_os_family() + "\nOS Arch: " + test_launcher.get_os_arch())
#test_launcher.BinaryManager.download_versions()
#print(test_launcher.BinaryManager.get_versions())
#test_launcher.BinaryManager.download_version_id("1.7.4")
#print(test_launcher.LibraryManager.official_id_to_path("org.apache.commons:commons-lang3:3.1"))
#print(test_launcher.LibraryManager.official_id_to_path("tv.twitch:twitch-platform:5.16", natives_extension="natives-windows-32"))
#print(test_launcher.LibraryManager.official_id_to_path("org.lwjgl.lwjgl:lwjgl-platform:2.9.0", natives_extension="natives-osx"))
#print('/'.join(test_launcher.LibraryManager.official_id_to_path("org.lwjgl.lwjgl:lwjgl-platform:2.9.1-nightly-20130708-debug3", natives_extension="natives-linux")))
#print(test_launcher.BinaryManager.get_version_file_paths("1.7.4", "vanilla"))
#test_launcher.LibraryManager.download_missing_official_libraries("1.7.4", status_function)
#test_launcher.AssetManager.download_asset_index("1.7.4")
#test_launcher.AssetManager.download_missing_assets("1.7.4", status_function)
#print(test_launcher.AssetManager.get_binary_assets_id("1.7.4"))
#test_launcher.AssetManager.download_asset_index("legacy")
#test_launcher.AssetManager.download_missing_assets("legacy", status_function)
#print(test_launcher.LibraryManager.get_version_dependencies("1.7.4"))
#test_launcher.ProfileManager.add_profile("Latest")

test_launcher.ProfileManager.get_profile_instance("Latest").launch_version("1.7.4", "vanilla")

# 1.5.2 launching

#test_launcher.BinaryManager.download_official_version_id("1.5.2")
#test_launcher.LibraryManager.download_missing_official_libraries("1.5.2", status_function)
#test_launcher.AssetManager.download_missing_assets("legacy", status_function)
#test_launcher.ProfileManager.add_profile("Old_1.5.2")
#test_launcher.ProfileManager.get_profile_instance("Old_1.5.2").launch_version("1.5.2", "vanilla")

#test_launcher.ProfileManager.get_profile_instance("Old_1.5.2").launch_version("1.5.2_Custom", "custom")
'''
