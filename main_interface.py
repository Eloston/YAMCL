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
import argparse
import traceback
import pathlib
from PySide import QtCore, QtGui

import yamcl.main

import graphical_interface.MainGUI

class DisplayExceptionDialog(QtGui.QDialog):
    def __init__(self, *args):
        super(DisplayExceptionDialog, self).__init__()

        exception_details = QtGui.QTextBrowser()
        exception_details.setPlainText(''.join(traceback.format_exception(*args)))

        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        buttonBox.button(QtGui.QDialogButtonBox.Close).clicked.connect(self.reject)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(QtGui.QLabel("YAMCL has encountered an unusual error. Details are below"))
        main_layout.addWidget(exception_details)
        main_layout.addWidget(QtGui.QLabel("Depending on the operation, it may or may not cause data corruption."))
        main_layout.addWidget(buttonBox)

        self.setLayout(main_layout)

        self.setWindowTitle("YAMCL: Error")

ExceptionDialog = None
def exception_dialog_hook(*args):
    global ExceptionDialog
    ExceptionDialog = DisplayExceptionDialog(*args)
    ExceptionDialog.show()

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--data-path", help="Override path to YAMCL's data directory", type=str, default=str())
    arg_parser.add_argument("--java-path", help="Override the Java executable to use", type=str, default=str())
    arg_parser.add_argument("--disable-library-download-exclusive", help="Disables the downloading of libraries for the current platform only (default is enabled)", action="store_false", dest="library_download_exclusive")
    arg_parser.set_defaults(library_download_exclusive=True)
    arg_returns = arg_parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    splash_image_path = str(pathlib.Path(sys.argv[0]).parent.joinpath(pathlib.Path("splashscreen.png")))
    splash_screen = QtGui.QSplashScreen(QtGui.QPixmap(splash_image_path))
    splash_screen.show()
    app.processEvents()

    main_launcher = yamcl.main.Launcher()
    startup_status = None
    while not startup_status == "SUCCESS":
        startup_status = main_launcher.startup(data_path=arg_returns.data_path, java_command=arg_returns.java_path)
        if startup_status == "FAIL_DATACORRUPT":
            clicked_button = QtGui.QMessageBox.critical(splash_screen, "YAMCL Data Error", "Your YAMCL data at " + str(main_launcher.ROOT_PATH) + " is missing or corrupt.\nWould you like to initialize the directory? Click Cancel to exit YAMCL.", QtGui.QMessageBox.Yes | QtGui.QMessageBox.Cancel)
            if clicked_button == QtGui.QMessageBox.Yes:
                main_launcher.create_skeleton_structure()
            else:
                sys.exit()

    main_launcher.LibraryManager.set_download_exclusive(arg_returns.library_download_exclusive)
    if main_launcher.PlatformTools.get_java_path() == None:
        QtGui.QMessageBox.critical(splash_screen, "YAMCL: Java Error", "YAMCL was not able to find Java on your system, or your specified Java path is not valid. You will not be able to launch the game.", QtGui.QMessageBox.Ok)
    main_gui = graphical_interface.MainGUI.MainGUI(main_launcher)
    sys.excepthook = exception_dialog_hook
    main_gui.show()
    splash_screen.finish(main_gui)
    sys.exit(app.exec_())

