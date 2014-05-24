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

class NotesEditor(QtGui.QDialog):
    def __init__(self, profile_name, notes_content, set_notes_func, parent=None):
        super(NotesEditor, self).__init__(parent)

        self.set_notes = set_notes_func

        verticalLayout = QtGui.QVBoxLayout(self)
        self.EditorBox = QtGui.QTextEdit()
        self.EditorBox.setPlainText(notes_content)
        verticalLayout.addWidget(self.EditorBox)
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Discard | QtGui.QDialogButtonBox.Save)
        buttonBox.button(QtGui.QDialogButtonBox.Discard).clicked.connect(self._discard_changes)
        buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(self._save_changes)
        verticalLayout.addWidget(buttonBox)

        self.setLayout(verticalLayout)

        self.setWindowTitle("YAMCL: Notes Editor for: " + profile_name)

        self.rejected.connect(self._close_editor)

    def _discard_changes(self):
        clicked_button = QtGui.QMessageBox.question(self, "YAMCL: Discard Changes?", "You may have unsaved changes. Are you sure you want to close the editor?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if clicked_button == QtGui.QMessageBox.Yes:
            self.reject()

    def _save_changes(self):
        self.set_notes(self.EditorBox.toPlainText())
        self.reject()

    def _close_editor(self):
        self.close()
