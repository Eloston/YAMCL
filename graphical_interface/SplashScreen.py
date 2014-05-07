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

class SplashScreen(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SplashScreen, self).__init__(parent)

        splash_message_layout = QtGui.QHBoxLayout()
        splash_message_layout.setSpacing(0)
        splash_text = QtGui.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setWeight(75)
        font.setBold(True)
        splash_text.setFont(font)
        splash_text.setAlignment(QtCore.Qt.AlignCenter)
        splash_message_layout.addWidget(splash_text)
        self.setLayout(splash_message_layout)

        self.setWindowTitle("YAMCL: Loading...")
        splash_text.setText("YAMCL is Starting Up...")

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    splash_screen = SplashScreen()
    splash_screen.show()
    sys.exit(app.exec_())

