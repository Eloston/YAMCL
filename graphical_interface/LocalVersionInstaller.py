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

from yamcl.tools import FileTools

from PySide import QtCore, QtGui

class LocalVersionInstaller(QtGui.QDialog):
    def __init__(self, binary_manager, refresh_list_func, parent=None):
        super(LocalVersionInstaller, self).__init__(parent)

        self.BinaryManager = binary_manager
        self.refresh_list = refresh_list_func
        self.last_filebrowser_dir = str()

        name_layout = QtGui.QHBoxLayout()
        name_layout.addWidget(QtGui.QLabel("Name:"))
        self.name_textbox = QtGui.QLineEdit()
        name_layout.addWidget(self.name_textbox)

        jar_layout = QtGui.QHBoxLayout()
        jar_layout.addWidget(QtGui.QLabel("JAR Path:"))
        self.jar_textbox = QtGui.QLineEdit()
        jar_layout.addWidget(self.jar_textbox)
        jar_browse_button = QtGui.QPushButton("Browse")
        jar_browse_button.clicked.connect(self._browse_jar)
        jar_layout.addWidget(jar_browse_button)

        json_layout = QtGui.QHBoxLayout()
        json_layout.addWidget(QtGui.QLabel("JSON Path:"))
        self.json_textbox = QtGui.QLineEdit()
        json_layout.addWidget(self.json_textbox)
        json_browse_button = QtGui.QPushButton("Browse")
        json_browse_button.clicked.connect(self._browse_json)
        json_layout.addWidget(json_browse_button)

        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self._cancel_install)
        buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self._complete_install)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addLayout(name_layout)
        main_layout.addWidget(QtGui.QLabel("Specify paths to the custom version:"))
        main_layout.addLayout(jar_layout)
        main_layout.addLayout(json_layout)
        main_layout.addStretch()
        main_layout.addWidget(buttonBox)

        self.setLayout(main_layout)

        self.setWindowTitle("YAMCL: Local Storage Version Installer")

        self.rejected.connect(self._close_installer)

    def _get_filebrowser_path(self, dialog_title, file_filter=None):
        all_filters = "All Files(*)"
        if not file_filter == None:
            all_filters = file_filter + ";;" + all_filters
        file_name, current_filter = QtGui.QFileDialog.getOpenFileName(self, dialog_title, dir=self.last_filebrowser_dir, filter=all_filters)
        if file_name:
            self.last_filebrowser_dir = FileTools.dir_name(file_name)
            return file_name
        else:
            return None

    def _browse_jar(self):
        file_name = self._get_filebrowser_path("YAMCL: Browse JAR Path", "JAR Files (*.jar)")
        if not file_name == None:
            self.jar_textbox.setText(file_name)

    def _browse_json(self):
        file_name = self._get_filebrowser_path("YAMCL: Browse JSON Path", "JSON Files (*.json)")
        if not file_name == None:
            self.json_textbox.setText(file_name)

    def _cancel_install(self):
        clicked_button = QtGui.QMessageBox.question(self, "YAMCL: Cancel Install?", "Do you want to cancel the install?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if clicked_button == QtGui.QMessageBox.Yes:
            self.reject()

    def _path_validator(self, name, file_path):
        if FileTools.exists(file_path):
            if FileTools.is_file(file_path):
                return True
            else:
                QtGui.QMessageBox.critical(self, "YAMCL: " + name + " Path Error", name + " path '" + file_path + "' is not a regular file.")
                return False
        else:
            QtGui.QMessageBox.critical(self, "YAMCL: " + name + " Path Error", name + " path '" + file_path + "' does not exist.")

    def _complete_install(self):
        if not len(self.name_textbox.text()) > 0:
            QtGui.QMessageBox.critical(self, "YAMCL: Custom Version Name Blank", "You cannot leave the custom version name blank.", QtGui.QMessageBox.Ok)
            return
        if self.name_textbox.text() in self.BinaryManager.get_installed_versions()["custom"]:
            QtGui.QMessageBox.critical(self, "YAMCL: Custom Version Name Conflict", "Custom Version name '" + self.name_textbox.text() + "' already exists", QtGui.QMessageBox.Ok)
            return
        if self._path_validator("JAR", self.jar_textbox.text()) and self._path_validator("JSON", self.json_textbox.text()):
            self.BinaryManager.install_custom(self.name_textbox.text(), self.jar_textbox.text(), self.json_textbox.text())
            self.refresh_list()
            self.reject()

    def _close_installer(self):
        self.close()
