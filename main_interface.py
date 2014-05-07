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

import sys
from PySide import QtCore, QtGui

import yamcl.main

import graphical_interface.MainGUI
import graphical_interface.SplashScreen

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    splash_screen = graphical_interface.SplashScreen.SplashScreen()
    splash_screen.show()

    main_launcher = yamcl.main.Launcher()
    yamcl_data_path = str()
    startup_status = None
    while not startup_status == "SUCCESS":
        startup_status = main_launcher.startup(yamcl_data_path)
        if startup_status == "FAIL_DATACORRUPT":
            clicked_button = QtGui.QMessageBox.critical(splash_screen, "YAMCL Data Error", "Your YAMCL data at " + str(yamcl.main.DataPath(str())) + " is missing or corrupt.\nWould you like to initialize the directory? Click Cancel to exit YAMCL.", QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
            if clicked_button == QtGui.QMessageBox.Yes:
                main_launcher.create_skeleton_structure()
            else:
                splash_screen.close()
                sys.exit(app.exec_())
    splash_screen.close()

    main_gui = graphical_interface.MainGUI.MainGUI(main_launcher)
    main_gui.show()
    sys.exit(app.exec_())
