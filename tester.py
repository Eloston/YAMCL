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

import Launcher

Launcher.g_filesystem.setdatapath(os.path.dirname(os.path.abspath(__file__))+"/YAMCL_data")
Launcher.g_filesystem.initfilestructure()

a = Launcher.versionjsonparser()
print('List download result:', a.updatelist())
print('Latest versions:', a.getlatest())
print('List of snapshots:', a.getsnapshotlist())
print('List of releases:', a.getreleaselist())
print('List of betas:', a.getbetalist())
print('List of alphas:', a.getalphalist())

b = Launcher.binmanager()
b.readindex()
b.addvanillaversion("13w39b")
