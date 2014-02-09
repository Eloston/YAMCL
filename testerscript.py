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
test_launcher.startup()
print("Data Integrity Check Holding: " + str(test_launcher.FileTools.check_data_integrity()))
print("OS Family: " + test_launcher.get_os_family() + "\nOS Arch: " + test_launcher.get_os_arch())
#test_launcher.BinaryManager.download_versions()
#print(test_launcher.BinaryManager.get_versions())
#test_launcher.BinaryManager.download_version_id("1.7.4")
#test_launcher.BinaryManager.download_version_id("1.6")
print(test_launcher.LibraryManager.official_id_to_path("org.apache.commons:commons-lang3:3.1"))
print(test_launcher.LibraryManager.official_id_to_path("tv.twitch:twitch-platform:5.16", natives_extension="natives-windows-32"))
print(test_launcher.LibraryManager.official_id_to_path("org.lwjgl.lwjgl:lwjgl-platform:2.9.0", natives_extension="natives-osx"))
print('/'.join(test_launcher.LibraryManager.official_id_to_path("org.lwjgl.lwjgl:lwjgl-platform:2.9.1-nightly-20130708-debug3", natives_extension="natives-linux")))
print(test_launcher.BinaryManager.get_version_file_paths("1.7.4", "vanilla"))
#test_launcher.LibraryManager.download_missing_official_libraries("1.7.4", status_function)
