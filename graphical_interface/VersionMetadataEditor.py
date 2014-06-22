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

from graphical_interface import VersionLibraryEditor

from PySide import QtCore, QtGui

class VersionMetadataEditor(QtGui.QDialog):
    def __init__(self, library_manager, version_metadata, version_name, parent=None):
        super(VersionMetadataEditor, self).__init__(parent)

        self.LibraryManager = library_manager
        self.metadata = version_metadata

        self.id_textbox = QtGui.QLineEdit(self.metadata.get_id())
        id_textbox_layout = QtGui.QHBoxLayout()
        id_textbox_layout.addWidget(QtGui.QLabel("Internal ID:"))
        id_textbox_layout.addWidget(self.id_textbox)

        self.arguments_textbox = QtGui.QLineEdit(self.metadata.get_arguments())
        arguments_textbox_layout = QtGui.QHBoxLayout()
        arguments_textbox_layout.addWidget(QtGui.QLabel("Game Arguments:"))
        arguments_textbox_layout.addWidget(self.arguments_textbox)

        self.launcher_version_spinbox = QtGui.QSpinBox()
        self.launcher_version_spinbox.setValue(self.metadata.get_minimum_version())
        launcher_version_spinbox_layout = QtGui.QHBoxLayout()
        launcher_version_spinbox_layout.addWidget(QtGui.QLabel("Minimum launcher version:"))
        launcher_version_spinbox_layout.addWidget(self.launcher_version_spinbox)

        self.assets_textbox = QtGui.QLineEdit(self.metadata.get_assets_id())
        assets_textbox_layout = QtGui.QHBoxLayout()
        assets_textbox_layout.addWidget(QtGui.QLabel("Assets ID:"))
        assets_textbox_layout.addWidget(self.assets_textbox)

        self.launch_class_textbox = QtGui.QLineEdit(self.metadata.get_launch_class())
        launch_class_textbox_layout = QtGui.QHBoxLayout()
        launch_class_textbox_layout.addWidget(QtGui.QLabel("Launch class:"))
        launch_class_textbox_layout.addWidget(self.launch_class_textbox)

        library_model = QtGui.QStandardItemModel()
        self.library_list = QtGui.QListView()
        self.library_list.setModel(library_model)
        self.library_list.setSelectionModel(QtGui.QItemSelectionModel(library_model))
        self.library_list.selectionModel().currentChanged.connect(self._selected_library_change)

        add_library_button = QtGui.QPushButton("Add")
        add_library_button.clicked.connect(self._add_library)
        self.delete_library_button = QtGui.QPushButton("Delete")
        self.delete_library_button.clicked.connect(self._delete_library)
        self.delete_library_button.setEnabled(False)
        self.edit_library_button = QtGui.QPushButton("Edit")
        self.edit_library_button.clicked.connect(self._edit_library)
        self.edit_library_button.setEnabled(False)
        library_actions_layout = QtGui.QHBoxLayout()
        library_actions_layout.addWidget(add_library_button)
        library_actions_layout.addWidget(self.delete_library_button)
        library_actions_layout.addWidget(self.edit_library_button)

        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Discard | QtGui.QDialogButtonBox.Save)
        buttonBox.button(QtGui.QDialogButtonBox.Discard).clicked.connect(self._discard_changes)
        buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(self._save_changes)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addLayout(id_textbox_layout)
        main_layout.addLayout(arguments_textbox_layout)
        main_layout.addLayout(launcher_version_spinbox_layout)
        main_layout.addLayout(assets_textbox_layout)
        main_layout.addLayout(launch_class_textbox_layout)
        main_layout.addWidget(QtGui.QLabel("Libraries:"))
        main_layout.addWidget(self.library_list)
        main_layout.addLayout(library_actions_layout)
        main_layout.addWidget(buttonBox)

        self.setLayout(main_layout)

        self.setWindowTitle("YAMCL: Version Metadata Editor: " + version_name)

        self.rejected.connect(self._close_editor)

        self._populate_library_list()

    def _selected_library_change(self, index, previous):
        is_selected = isinstance(self.library_list.model().itemFromIndex(index), QtGui.QStandardItem)
        self.delete_library_button.setEnabled(is_selected)
        self.edit_library_button.setEnabled(is_selected)

    def _populate_library_list(self):
        self.library_list.model().clear()
        for library_metadata in self.metadata.get_library_metadatas():
            current_item = QtGui.QStandardItem(library_metadata.get_id())
            current_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            self.library_list.model().invisibleRootItem().appendRow(current_item)
        self.library_list.model().sort(0)

    def _add_library(self):
        unused_libraries = self.LibraryManager.get_all_library_ids()
        for library_metadata in self.metadata.get_library_metadatas():
            if library_metadata.get_id() in unused_libraries:
                unused_libraries.remove(library_metadata.get_id())
        new_library_id, success = QtGui.QInputDialog.getItem(self, "YAMCL: Add Library", "Specify a library to add:", unused_libraries, 0, False) # Tuple unpacking
        if success:
            library_metadata_editor = VersionLibraryEditor.VersionLibraryEditor(self.complete_add_library, library_id=new_library_id, parent=self)
            library_metadata_editor.show()

    def complete_add_library(self, library_id, rules_dict, natives_dict):
        self.metadata.add_library(library_id, rules_dict, natives_dict)
        self._populate_library_list()

    def _delete_library(self):
        current_library_id = self.library_list.model().itemFromIndex(self.library_list.currentIndex()).text()
        clicked_button = QtGui.QMessageBox.question(self, "YAMCL: Delete " + current_library_id, "Are you sure you want to delete version library '" + current_library_id + "'?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if clicked_button == QtGui.QMessageBox.Yes:
            self.metadata.delete_library(current_library_id)
            self._populate_library_list()

    def _edit_library(self):
        current_library_id = self.library_list.model().itemFromIndex(self.library_list.currentIndex()).text()
        for library_metadata in self.metadata.get_library_metadatas():
            if library_metadata.get_id() == current_library_id:
                library_metadata_editor = VersionLibraryEditor.VersionLibraryEditor(self.complete_edit_library, library_metadata=library_metadata, parent=self)
                library_metadata_editor.show()

    def complete_edit_library(self, library_metadata):
        self.metadata.import_library_metadata(library_metadata)
        self._populate_library_list()

    def _discard_changes(self):
        clicked_button = QtGui.QMessageBox.question(self, "YAMCL: Discard Changes?", "You may have unsaved changes. Are you sure you want to close the editor?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if clicked_button == QtGui.QMessageBox.Yes:
            self.reject()

    def _save_changes(self):
        self.metadata.set_id(self.id_textbox.text())
        self.metadata.set_arguments(self.arguments_textbox.text())
        self.metadata.set_minimum_version(self.launcher_version_spinbox.value())
        self.metadata.set_assets_id(self.assets_textbox.text())
        self.metadata.set_launch_class(self.launch_class_textbox.text())
        self.metadata.flush_info()
        self.reject()

    def _close_editor(self):
        self.close()
