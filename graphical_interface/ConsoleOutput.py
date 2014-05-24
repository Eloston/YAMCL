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

import threading

from PySide import QtCore, QtGui

class UpdateEvent(QtCore.QObject):
    updated = QtCore.Signal(str)

    def __init__(self):
        QtCore.QObject.__init__(self)

    def update(self, text):
        self.updated.emit(text)

class GameOutput(QtGui.QDialog):
    def __init__(self, profile_name, file_obj, parent=None):
        super(GameOutput, self).__init__(parent)

        self.output_obj = file_obj

        verticalLayout = QtGui.QVBoxLayout(self)
        self.StandardOutputText = QtGui.QTextBrowser()
        self.StandardOutputText.setWordWrapMode(QtGui.QTextOption.NoWrap)
        verticalLayout.addWidget(self.StandardOutputText)
        buttonBox = QtGui.QDialogButtonBox(self)
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        buttonBox.button(QtGui.QDialogButtonBox.Close).clicked.connect(self.reject)
        verticalLayout.addWidget(buttonBox)

        self.setLayout(verticalLayout)

        self.resize(500, 400)

        self.setWindowTitle("YAMCL: Console Output for " + profile_name)

        self.rejected.connect(self._hide_output)

        self.screen_update_thread = threading.Thread(target=self._update_loop)
        self.screen_update_thread.start()

        self.screen_update_event = UpdateEvent()
        self.screen_update_event.updated.connect(self._screen_update, type=QtCore.Qt.QueuedConnection)

    def _update_loop(self):
        while True:
            line = self.output_obj.readline()
            if not line:
                break
            self.screen_update_event.update(line)

    @QtCore.Slot(str)
    def _screen_update(self, text):
        self.StandardOutputText.append(text.rstrip("\n"))
        self.StandardOutputText.moveCursor(QtGui.QTextCursor.End)
        self.StandardOutputText.moveCursor(QtGui.QTextCursor.StartOfLine)

    def _hide_output(self):
        self.hide()
