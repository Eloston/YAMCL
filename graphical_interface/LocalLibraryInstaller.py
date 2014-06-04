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
        self.library_type_combobox = QtGui.QComboBox()
        self.library_type_combobox.addItems(["JAR File", "Natives"])
        self.library_type_combobox.currentIndexChanged[str].connect(self._type_changed)
        library_type_layout.addWidget(self.library_type_combobox)

        self.jar_settings_groupbox = QtGui.QGroupBox("Jar Settings")
        jar_settings_groupbox_layout = QtGui.QVBoxLayout()
        jar_path_layout = QtGui.QHBoxLayout()
        jar_path_layout.addWidget(QtGui.QLabel("Path:"))
        self.jar_path_textbox = QtGui.QLineEdit()
        jar_path_layout.addWidget(self.jar_path_textbox)
        jar_browse_button = QtGui.QPushButton("Browse")
        jar_browse_button.clicked.connect(self._browse_jar)
        jar_path_layout.addWidget(jar_browse_button)
        self.jar_destination_textbox = QtGui.QLineEdit()
        jar_destination_browse_button = QtGui.QPushButton("Browse")
        jar_destination_browse_button.clicked.connect(self._browse_jar_destination)
        jar_destination_layout = QtGui.QHBoxLayout()
        jar_destination_layout.addWidget(QtGui.QLabel("Destination:"))
        jar_destination_layout.addWidget(self.jar_destination_textbox)
        jar_destination_layout.addWidget(jar_destination_browse_button)
        jar_settings_groupbox_layout.addLayout(jar_path_layout)
        jar_settings_groupbox_layout.addLayout(jar_destination_layout)
        self.jar_settings_groupbox.setLayout(jar_settings_groupbox_layout)

        self.natives_settings_groupbox = QtGui.QGroupBox("Natives Settings")
        self.natives_settings_groupbox.setEnabled(False)
        natives_dir_model = QtGui.QStandardItemModel()
        self.natives_dir_list = QtGui.QListView()
        self.natives_dir_list.setModel(natives_dir_model)
        self.natives_dir_list.setSelectionModel(QtGui.QItemSelectionModel(natives_dir_model))
        self.natives_dir_list.selectionModel().currentChanged.connect(self._selected_native_change)
        add_native_button = QtGui.QPushButton("Add Path")
        add_native_button.clicked.connect(self._add_native_path)
        self.remove_native_button = QtGui.QPushButton("Remove Path")
        self.remove_native_button.clicked.connect(self._remove_native_path)
        self.remove_native_button.setEnabled(False)
        natives_action_buttons_layout = QtGui.QHBoxLayout()
        natives_action_buttons_layout.addWidget(add_native_button)
        natives_action_buttons_layout.addWidget(self.remove_native_button)
        self.natives_destination_textbox = QtGui.QLineEdit()
        natives_destination_browse_button = QtGui.QPushButton("Browse")
        natives_destination_browse_button.clicked.connect(self._browse_natives_destination)
        natives_destination_layout = QtGui.QHBoxLayout()
        natives_destination_layout.addWidget(QtGui.QLabel("Destination:"))
        natives_destination_layout.addWidget(self.natives_destination_textbox)
        natives_destination_layout.addWidget(natives_destination_browse_button)
        natives_settings_groupbox_layout = QtGui.QVBoxLayout()
        natives_settings_groupbox_layout.addWidget(self.natives_dir_list)
        natives_settings_groupbox_layout.addLayout(natives_action_buttons_layout)
        natives_settings_groupbox_layout.addLayout(natives_destination_layout)
        self.natives_settings_groupbox.setLayout(natives_settings_groupbox_layout)

        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        buttonBox.button(QtGui.QDialogButtonBox.Cancel).clicked.connect(self._cancel_install)
        buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked.connect(self._complete_install)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addLayout(name_layout)
        main_layout.addLayout(library_type_layout)
        main_layout.addWidget(self.jar_settings_groupbox)
        main_layout.addWidget(self.natives_settings_groupbox)
        main_layout.addWidget(buttonBox)

        self.setLayout(main_layout)

        self.setWindowTitle("YAMCL: Local Storage Library Installer")

        self.rejected.connect(self._close_installer)

    def _selected_type(self):
        tmp_text = self.library_type_combobox.currentText()
        if len(tmp_text) == 0:
            return None
        else:
            return tmp_text

    def _type_changed(self, new_text):
        self.natives_settings_groupbox.setEnabled(new_text == "Natives")
        self.jar_settings_groupbox.setEnabled(new_text == "JAR File")

    def _selected_native_change(self, index, previous):
        is_selected = isinstance(self.natives_dir_list.model().itemFromIndex(index), QtGui.QStandardItem)
        self.remove_native_button.setEnabled(is_selected)

    def _get_natives_list(self):
        natives_list = list()
        for current_item in self.natives_dir_list.model().findItems(str(), flags=QtCore.Qt.MatchStartsWith):
            natives_list.append(current_item.text())
        return natives_list

    def _native_exists(self, native_dir):
        return len(self.natives_dir_list.model().findItems(native_dir)) > 0

    def _add_native_path(self):
        new_directory = self._get_filebrowser_dir_path("YAMCL: Select Natives Directory")
        if self._native_exists(new_directory):
            QtGui.QMessageBox.critical(self, "YAMCL: Native Path Exists", "Natives directory '" + new_directory + "' is already added.", QtGui.QMessageBox.Ok)
        else:
            self.last_filebrowser_dir = FileTools.dir_name(new_directory)
            self.natives_dir_list.model().appendRow(QtGui.QStandardItem(new_directory))

    def _remove_native_path(self):
        self.natives_dir_list.model().takeRow(self.natives_dir_list.currentIndex().row())

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

    def _get_filebrowser_save_path(self, dialog_title, file_filter=None, last_dir=None):
        if last_dir == None:
            last_dir = self.last_filebrowser_dir
        all_filters = "All Files(*)"
        if not file_filter == None:
            all_filters = file_filter + ";;" + all_filters
        file_name, current_filter = QtGui.QFileDialog.getSaveFileName(self, dialog_title, dir=last_dir, filter=all_filters)
        if file_name:
            self.last_filebrowser_dir = FileTools.dir_name(file_name)
            return file_name
        else:
            return None

    def _get_filebrowser_dir_path(self, dialog_title, last_dir=None):
        if last_dir == None:
            last_dir = self.last_filebrowser_dir
        directory = QtGui.QFileDialog.getExistingDirectory(self, dialog_title, dir=last_dir)
        if directory:
            self._last_filebrowser_dir = directory
            return directory
        else:
            return None

    def _browse_jar(self):
        file_name = self._get_filebrowser_file_path("YAMCL: Browse JAR Path", "JAR Files (*.jar)")
        if not file_name == None:
            self.jar_path_textbox.setText(file_name)

    def _browse_jar_destination(self):
        file_name = self._get_filebrowser_save_path("YAMCL: Get JAR Save File", "JAR Files (*.jar)", str(self.LibraryManager.BASE_PATH))
        if not file_name == None:
            self.jar_destination_textbox.setText(file_name)

    def _browse_natives_destination(self):
        destination_dir = self._get_filebrowser_dir_path("YAMCL: Get Natives Destination Directory", str(self.LibraryManager.BASE_PATH))
        if not destination_dir == None:
            self.natives_destination_textbox.setText(destination_dir)

    def _cancel_install(self):
        clicked_button = QtGui.QMessageBox.question(self, "YAMCL: Cancel Install?", "Do you want to cancel the install?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if clicked_button == QtGui.QMessageBox.Yes:
            self.reject()

    def _file_exists(self, name, file_path):
        if FileTools.exists(file_path):
            if FileTools.is_file(file_path):
                return True
            else:
                QtGui.QMessageBox.critical(self, "YAMCL: " + name + " Path Error", name + " path '" + file_path + "' is not a regular file.")
                return False
        else:
            QtGui.QMessageBox.critical(self, "YAMCL: " + name + " Path Error", name + " path '" + file_path + "' does not exist.")

    def _dir_exists(self, name, dir_path):
        if FileTools.exists(dir_path):
            if FileTools.is_dir(dir_path):
                return True
            else:
                QtGui.QMessageBox.critical(self, "YAMCL: " + name + " Path Error", name + " path '" + dir_path + "' is not a directory.")
                return False
        else:
            QtGui.QMessageBox.critical(self, "YAMCL: " + name + " Path Error", name + " path '" + dir_path + "' does not exist.")

    def _complete_install(self):
        if not len(self.name_textbox.text()) > 0:
            QtGui.QMessageBox.critical(self, "YAMCL: Library Name Blank", "You cannot leave the library name blank.", QtGui.QMessageBox.Ok)
            return
        if self.name_textbox.text() in self.LibraryManager.get_all_library_ids():
            QtGui.QMessageBox.critical(self, "YAMCL: Library Name Conflict", "Library name '" + self.name_textbox.text() + "' already exists", QtGui.QMessageBox.Ok)
            return
        is_natives = self.library_type_combobox.currentText() == "Natives"
        if is_natives:
            all_native_dirs = self._get_natives_list()
            if len(all_native_dirs) == 0:
                QtGui.QMessageBox.critical(self, "YAMCL: No Natives Directories Supplied", "You have not selected any natives directories to install.", QtGui.QMessageBox.Ok)
                return
            for current_dir in all_native_dirs:
                if not self._dir_exists("Directory", current_dir):
                    return
            if not self._dir_exists("Directory", self.natives_destination_textbox.text()):
                return
            self.LibraryManager.add_local(self.name_textbox.text(), True, all_native_dirs, self.natives_destination_textbox.text())
        else:
            if self._file_exists("JAR", self.jar_path_textbox.text()):
                if len(self.jar_destination_textbox.text()) > 0:
                    self.LibraryManager.add_local(self.name_textbox.text(), False, [self.jar_path_textbox.text()], self.jar_destination_textbox.text())
                else:
                    QtGui.QMessageBox.critical(self, "YAMCL: No JAR Destination Specified", "You have not specified a destination JAR file", QtGui.QMessageBox.Ok)
                    return
            else:
                return
        self.refresh_list()
        self.reject()

    def _close_installer(self):
        self.close()
