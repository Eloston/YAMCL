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

from PySide import QtCore, QtGui

class VersionLibraryEditor(QtGui.QDialog):
    def __init__(self, save_func, library_metadata=None, library_id=None, parent=None):
        super(VersionLibraryEditor, self).__init__(parent)

        self.is_new = (library_metadata is None)
        if self.is_new:
            self.id = library_id
        else:
            self.metadata = library_metadata

        self.save_function = save_func

        rules_groupbox = QtGui.QGroupBox("Rules")
        self.windows_checkbox = QtGui.QCheckBox("windows")
        self.linux_checkbox = QtGui.QCheckBox("linux")
        self.osx_checkbox = QtGui.QCheckBox("osx")
        rules_groupbox_layout = QtGui.QVBoxLayout()
        rules_groupbox_layout.addWidget(self.windows_checkbox)
        rules_groupbox_layout.addWidget(self.linux_checkbox)
        rules_groupbox_layout.addWidget(self.osx_checkbox)
        if not self.is_new:
            if self.metadata.get_rules()["windows"]:
                self.windows_checkbox.setCheckState(QtCore.Qt.Checked)
            if self.metadata.get_rules()["linux"]:
                self.linux_checkbox.setCheckState(QtCore.Qt.Checked)
            if self.metadata.get_rules()["osx"]:
                self.osx_checkbox.setCheckState(QtCore.Qt.Checked)
        rules_groupbox.setLayout(rules_groupbox_layout)

        self.natives_groupbox = QtGui.QGroupBox("Natives Extensions")
        self.natives_groupbox.setCheckable(True)
        self.natives_groupbox.setChecked(False)
        self.windows_extension = QtGui.QLineEdit()
        self.linux_extension = QtGui.QLineEdit()
        self.osx_extension = QtGui.QLineEdit()
        if not self.is_new:
            if self.metadata.is_natives():
                self.natives_groupbox.setChecked(True)
                if "windows" in self.metadata.get_raw_natives_extensions():
                    self.windows_extension.setText(self.metadata.get_raw_natives_extensions()["windows"])
                if "linux" in self.metadata.get_raw_natives_extensions():
                    self.linux_extension.setText(self.metadata.get_raw_natives_extensions()["linux"])
                if "osx" in self.metadata.get_raw_natives_extensions():
                    self.osx_extension.setText(self.metadata.get_raw_natives_extensions()["osx"])
        natives_groupbox_layout = QtGui.QVBoxLayout()
        windows_extension_layout = QtGui.QHBoxLayout()
        windows_extension_layout.addWidget(QtGui.QLabel("windows:"))
        windows_extension_layout.addWidget(self.windows_extension)
        natives_groupbox_layout.addLayout(windows_extension_layout)
        linux_extension_layout = QtGui.QHBoxLayout()
        linux_extension_layout.addWidget(QtGui.QLabel("linux:"))
        linux_extension_layout.addWidget(self.linux_extension)
        natives_groupbox_layout.addLayout(linux_extension_layout)
        osx_extension_layout = QtGui.QHBoxLayout()
        osx_extension_layout.addWidget(QtGui.QLabel("osx:"))
        osx_extension_layout.addWidget(self.osx_extension)
        natives_groupbox_layout.addLayout(osx_extension_layout)
        self.natives_groupbox.setLayout(natives_groupbox_layout)

        buttonBox = QtGui.QDialogButtonBox()
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Discard | QtGui.QDialogButtonBox.Save)
        buttonBox.button(QtGui.QDialogButtonBox.Discard).clicked.connect(self._discard_changes)
        buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(self._save_changes)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(rules_groupbox)
        main_layout.addWidget(self.natives_groupbox)
        main_layout.addStretch()
        main_layout.addWidget(buttonBox)

        self.setLayout(main_layout)

        if self.is_new:
            self.setWindowTitle("YAMCL: Version Library Metadata Editor: " + library_id)
        else:
            self.setWindowTitle("YAMCL: Version Library Metadata Editor: " + library_metadata.get_id())

        self.rejected.connect(self._close_editor)

    def _discard_changes(self):
        clicked_button = QtGui.QMessageBox.question(self, "YAMCL: Discard Changes?", "You may have unsaved changes. Are you sure you want to close the editor?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if clicked_button == QtGui.QMessageBox.Yes:
            self.reject()

    def _save_changes(self):
        rules_dict = dict()
        rules_dict["windows"] = self.windows_checkbox.isChecked()
        rules_dict["linux"] = self.linux_checkbox.isChecked()
        rules_dict["osx"] = self.osx_checkbox.isChecked()
        natives_dict = None
        if self.natives_groupbox.isChecked():
            natives_dict = dict()
            if rules_dict["windows"]:
                natives_dict["windows"] = self.windows_extension.text()
            if rules_dict["linux"]:
                natives_dict["linux"] = self.linux_extension.text()
            if rules_dict["osx"]:
                natives_dict["osx"] = self.osx_extension.text()
            if len(natives_dict) == 0:
                natives_dict = None
        if self.is_new:
            self.save_function(self.id, rules_dict, natives_dict)
        else:
            self.metadata.set_rules(rules_dict)
            if not natives_dict is None:
                self.metadata.set_natives_extensions(natives_dict)
            self.save_function(self.metadata)
        self.reject()

    def _close_editor(self):
        self.close()
