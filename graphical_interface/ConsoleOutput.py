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

class GameOutput(QtGui.QDialog):
    def __init__(self, parent=None):
        super(GameOutput, self).__init__(parent)

        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.StandardOutputText = QtGui.QTextBrowser(self)
        self.verticalLayout.addWidget(self.StandardOutputText)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.verticalLayout.addWidget(self.buttonBox)

        self.setLayout(self.verticalLayout)

        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), GameOutput.accept)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), GameOutput.reject)
        #QtCore.QMetaObject.connectSlotsByName(self)

        self.setWindowTitle("YAMCL: Console Output for <None>")

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    game_output = GameOutput()
    game_output.show()
    sys.exit(app.exec_())

