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

import yamcl.main

test_launcher = yamcl.main.Launcher()
test_launcher.startup()
print(test_launcher.FileTools.check_data_integrity())
print("OS Family: " + test_launcher.get_os_family() + "\nOS Arch: " + test_launcher.get_os_arch())
#test_launcher.BinaryManager.download_versions()
#print(test_launcher.BinaryManager.get_versions())
#test_launcher.BinaryManager.download_version_id("1.7.4")
test_launcher.BinaryManager.download_version_id("1.6")
