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
