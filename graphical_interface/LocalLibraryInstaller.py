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

class LocalLibraryInstaller(QtGui.QDialog):
    def __init__(self, library_manager, refresh_list_func, parent=None):
        super(LocalLibraryInstaller, self).__init__(parent)

        self.LibraryManager = library_manager
        self.refresh_list = refresh_list_func
        self.last_filebrowser_dir = str()

        name_layout = QtGui.QHBoxLayout()
        name_layout.addWidget(QtGui.QLabel("Name:"))
        self.name_textbox = QtGui.QLineEdit()
        name_layout.addWidget(self.name_textbox)

        library_type_layout = QtGui.QHBoxLayout()
        library_type_layout.addWidget(QtGui.QLabel("Library Type:"))
        self.library_type_combobox = QtGui.QComboBox()
        library_type_layout.addWidget(self.library_type_combobox)

        jar_settings_groupbox = QtGui.QGroupBox("Jar Settings")
        jar_settings_groupbox_layout = QtGui.QHBoxLayout()
        jar_settings_groupbox_layout.addWidget(QtGui.QLabel("Path:"))
        self.jar_path_textbox = QtGui.QLineEdit()
        jar_settings_groupbox_layout.addWidget(self.jar_path_textbox)
        jar_browse_button = QtGui.QPushButton("Browse")
        jar_browse_button.clicked.connect(self._browse_jar)
        jar_settings_groupbox_layout.addWidget(jar_browse_button)
        jar_settings_groupbox.setLayout(jar_settings_groupbox_layout)

        natives_settings_groupbox = QtGui.QGroupBox("Natives Settings")
        natives_dir_model = QtGui.QStandardItemModel()
        self.natives_dir_list = QtGui.QListView()
        self.natives_dir_list.setModel(natives_dir_model)
        self.natives_dir_list.setSelectionModel(QtGui.QItemSelectionModel(natives_dir_model))
        self.natives_dir_list.selectionModel().currentChanged.connect(self._selected_native_change)
        self.add_native_button = QtGui.QPushButton("Add Path")
        self.add_native_button.setEnabled(False)
        self.remove_native_button = QtGui.QPushButton("Remove Path")
        self.remove_native_button.setEnabled(False)
        natives_action_buttons_layout = QtGui.QHBoxLayout()
        natives_action_buttons_layout.addWidget(self.add_native_button)
        natives_action_buttons_layout.addWidget(self.remove_native_button)
        natives_settings_groupbox_layout = QtGui.QVBoxLayout()
        natives_settings_groupbox_layout.addWidget(self.natives_dir_list)
        natives_settings_groupbox_layout.addLayout(natives_action_buttons_layout)
        natives_settings_groupbox.setLayout(natives_settings_groupbox_layout)

        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self._cancel_install)
        buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self._complete_install)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addLayout(name_layout)
        main_layout.addLayout(library_type_layout)
        main_layout.addWidget(jar_settings_groupbox)
        main_layout.addWidget(natives_settings_groupbox)
        main_layout.addWidget(buttonBox)

        self.setLayout(main_layout)

        self.setWindowTitle("YAMCL: Local Storage Library Installer")

        self.rejected.connect(self._close_installer)

    def _selected_native_change(self, index, previous):
        is_selected = isinstance(self.natives_dir_list.model().itemFromIndex(index), QtGui.QStandardItem)
        self.add_native_button.setEnabled(is_selected)
        self.remove_native_button.setEnabled(is_selected)

    def _get_filebrowser_file_path(self, dialog_title, file_filter=None):
        all_filters = "All Files(*)"
        if not file_filter == None:
            all_filters = file_filter + ";;" + all_filters
        file_name, current_filter = QtGui.QFileDialog.getOpenFileName(self, dialog_title, dir=self.last_filebrowser_dir, filter=all_filters)
        if file_name:
            self.last_filebrowser_dir = FileTools.dir_name(file_name)
            return file_name
        else:
            return None

    def _get_filebrowser_dir_path(self, dialog_title):
        directory = QtGui.QFileDialog.getExistingDirectory(self, dialog_title, dir=self.last_filebrowser_dir)
        if directory:
            self._last_filebrowser_dir = directory
            return directory
        else:
            return None

    def _browse_jar(self):
        file_name = self._get_filebrowser_file_path("YAMCL: Browse JAR Path", "JAR Files (*.jar)")
        if not file_name == None:
            self.jar_path_textbox.setText(file_name)

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
            QtGui.QMessageBox.critical(self, "YAMCL: Library Name Blank", "You cannot leave the library name blank.", QtGui.QMessageBox.Ok)
            return
        if self.name_textbox.text() in self.LibraryManager.get_all_library_ids():
            QtGui.QMessageBox.critical(self, "YAMCL: Library Name Conflict", "Library name '" + self.name_textbox.text() + "' already exists", QtGui.QMessageBox.Ok)
            return
        if self._path_validator("JAR", self.jar_textbox.text()) and self._path_validator("JSON", self.json_textbox.text()):
            self.refresh_list()
            self.reject()

    def _close_installer(self):
        self.close()
