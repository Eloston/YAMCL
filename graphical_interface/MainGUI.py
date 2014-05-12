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

import os
import subprocess

from PySide import QtCore, QtGui

class AccountTab(QtGui.QWidget):
    def __init__(self, launcher_obj, parent=None):
        super(AccountTab, self).__init__(parent)
        self.Launcher = launcher_obj

        # Mode Toggling

        self.offline_radio = QtGui.QRadioButton("Offline")
        self.offline_radio.setChecked(True)
        self.offline_radio.toggled.connect(self._toggle_mode)
        self.online_radio = QtGui.QRadioButton("Online")

        mode_groupbox = QtGui.QGroupBox("Mode")
        mode_groupbox_layout = QtGui.QVBoxLayout()
        mode_groupbox_layout.addWidget(self.offline_radio)
        mode_groupbox_layout.addWidget(self.online_radio)
        mode_groupbox.setLayout(mode_groupbox_layout)

        # Offline Settings

        self.offline_username = QtGui.QLineEdit()
        self.offline_username.setText(self.Launcher.AccountManager.get_game_username())
        set_username_button = QtGui.QPushButton("Set Username")
        set_username_button.clicked.connect(self._set_offline_username)

        self.offline_settings_groupbox = QtGui.QGroupBox("Offline Settings")
        offline_settings_groupbox_layout = QtGui.QHBoxLayout()
        offline_settings_groupbox_layout.addWidget(QtGui.QLabel("In-game Username:"))
        offline_settings_groupbox_layout.addWidget(self.offline_username)
        offline_settings_groupbox_layout.addWidget(set_username_button)
        self.offline_settings_groupbox.setLayout(offline_settings_groupbox_layout)

        # Online Settings

        self.online_username = QtGui.QLineEdit()
        online_username_layout = QtGui.QHBoxLayout()
        online_username_layout.addWidget(QtGui.QLabel("Username:"))
        online_username_layout.addWidget(self.online_username)

        self.online_password = QtGui.QLineEdit()
        self.online_password.setEchoMode(QtGui.QLineEdit.Password)
        online_password_layout = QtGui.QHBoxLayout()
        online_password_layout.addWidget(QtGui.QLabel("Password:"))
        online_password_layout.addWidget(self.online_password)

        self.signin_button = QtGui.QPushButton("Sign in")
        self.signin_button.clicked.connect(self._signin)
        self.signout_button = QtGui.QPushButton("Sign out")
        self.signout_button.clicked.connect(self._signout)
        self.signout_button.setEnabled(False)
        online_buttons_layout = QtGui.QHBoxLayout()
        online_buttons_layout.addStretch()
        online_buttons_layout.addWidget(self.signin_button)
        online_buttons_layout.addWidget(self.signout_button)

        self.online_settings_groupbox = QtGui.QGroupBox("Online Settings")
        self.online_settings_groupbox.setEnabled(False)
        online_settings_groupbox_layout = QtGui.QVBoxLayout()
        online_settings_groupbox_layout.addLayout(online_username_layout)
        online_settings_groupbox_layout.addLayout(online_password_layout)
        online_settings_groupbox_layout.addLayout(online_buttons_layout)
        self.online_settings_groupbox.setLayout(online_settings_groupbox_layout)

        # Construct final layout

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(mode_groupbox)
        main_layout.addWidget(self.offline_settings_groupbox)
        main_layout.addWidget(self.online_settings_groupbox)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def _toggle_mode(self):
        if self.offline_radio.isChecked():
            self.offline_settings_groupbox.setEnabled(True)
            self.online_settings_groupbox.setEnabled(False)
        elif self.online_radio.isChecked():
            # TODO: Implement when authentication has been implemented
            QtGui.QMessageBox.critical(self, "YAMCL: Account Error", "Online mode has not bee implemented yet.", QtGui.QMessageBox.Ok)
            self.online_radio.setChecked(False)
            self.offline_radio.setChecked(True)
            #self.offline_settings_groupbox.setEnabled(False)
            #self.online_settings_groupbox.setEnabled(True)

    def _set_offline_username(self):
        print("Current Offline Username: " + self.offline_username.text())
        self.Launcher.AccountManager.set_game_username(self.offline_username.text())

    def _signin(self):
        # TODO: Implement when authentication has been implemented
        print("Username: " + self.online_username.text())
        print("Password: " + self.online_password.text())
        self.online_password.setText(str())
        self.online_username.setEnabled(False)
        self.online_password.setEnabled(False)
        self.signin_button.setEnabled(False)
        self.signout_button.setEnabled(True)

    def _signout(self):
        # TODO: Implement when authentication has been implemented
        print("Signing out")
        self.online_username.setEnabled(True)
        self.online_password.setEnabled(True)
        self.signin_button.setEnabled(True)
        self.signout_button.setEnabled(False)

class ProfilesTab(QtGui.QWidget):
    def __init__(self, launcher_obj, parent=None):
        super(ProfilesTab, self).__init__(parent)
        self.Launcher = launcher_obj

        self.open_profile_instances = list()

        profile_instance_groupbox = QtGui.QGroupBox("Open Profiles")
        self.profile_instance_tabwidget = QtGui.QTabWidget()
        self.profile_instance_tabwidget.setTabsClosable(True)
        self.profile_instance_tabwidget.setMovable(True)
        self.profile_instance_tabwidget.tabCloseRequested.connect(self._close_tab)
        profile_instance_groupbox_layout = QtGui.QVBoxLayout()
        profile_instance_groupbox_layout.addWidget(self.profile_instance_tabwidget)
        profile_instance_groupbox.setLayout(profile_instance_groupbox_layout)

        profile_actions_groupbox = QtGui.QGroupBox("Profile Actions")
        open_profile_button = QtGui.QPushButton("Open Profile")
        open_profile_button.clicked.connect(self._open_profile_tab)
        new_profile_button = QtGui.QPushButton("New Profile")
        delete_profile_button = QtGui.QPushButton("Delete Profile")
        rename_profile_button = QtGui.QPushButton("Rename Profile")
        profile_actions_groupbox_layout = QtGui.QHBoxLayout()
        profile_actions_groupbox_layout.addWidget(open_profile_button)
        profile_actions_groupbox_layout.addStretch()
        profile_actions_groupbox_layout.addWidget(new_profile_button)
        profile_actions_groupbox_layout.addWidget(delete_profile_button)
        profile_actions_groupbox_layout.addWidget(rename_profile_button)
        profile_actions_groupbox.setLayout(profile_actions_groupbox_layout)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(profile_instance_groupbox)
        main_layout.addWidget(profile_actions_groupbox)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def _open_profile_tab(self):
        unopened_profile_list = list()
        all_profiles = self.Launcher.ProfileManager.get_profile_list()
        for current_profile in all_profiles:
            if not current_profile in self.open_profile_instances:
                unopened_profile_list.append(current_profile)
        if len(unopened_profile_list) == 0:
            QtGui.QMessageBox.critical(self, "YAMCL: Open Profile Error", "There are no more profiles left to open.", QtGui.QMessageBox.Ok)
            return
        profile_name, success = QtGui.QInputDialog.getItem(self, "YAMCL: Open Profile", "Specify a Profile:", unopened_profile_list, 0, False) # Tuple unpacking
        if success:
            if profile_name in self.open_profile_instances:
                QtGui.QMessageBox.critical(self, "YAMCL: Open Profile Error", "Profile " + profile_name + " is already open", QtGui.QMessageBox.Ok)
            else:
                tmp_profile_instance = self.Launcher.ProfileManager.get_profile_instance(profile_name)
                tmp_profile_tab = ProfileInstanceTab(self.Launcher, tmp_profile_instance)
                self.open_profile_instances.append(profile_name)
                self.profile_instance_tabwidget.addTab(tmp_profile_tab, profile_name)

    def _close_tab(self, index):
        profile_tab = self.profile_instance_tabwidget.widget(index)
        self.open_profile_instances.remove(profile_tab.get_name())
        profile_tab.close()
        self.profile_instance_tabwidget.removeTab(index)

class ProfileInstanceTab(QtGui.QWidget):
    def __init__(self, launcher_obj, instance_obj, parent=None):
        super(ProfileInstanceTab, self).__init__(parent)
        self.Launcher = launcher_obj
        self.ProfileInstance = instance_obj

        notes_groupbox = QtGui.QGroupBox("Notes")
        self.notes_preview = QtGui.QTextBrowser()
        edit_notes_button = QtGui.QPushButton("Edit Notes")
        notes_groupbox_layout = QtGui.QHBoxLayout()
        notes_groupbox_layout.addWidget(self.notes_preview)
        notes_groupbox_layout.addWidget(edit_notes_button)
        notes_groupbox.setLayout(notes_groupbox_layout)

        specify_version_groupbox = QtGui.QGroupBox("Version to Launch")
        self.type_combobox = QtGui.QComboBox()
        self.type_combobox.currentIndexChanged[str].connect(self._type_changed)
        self.id_combobox = QtGui.QComboBox()
        self.id_combobox.currentIndexChanged[str].connect(self._id_changed)
        specify_version_groupbox_layout = QtGui.QHBoxLayout()
        specify_version_groupbox_layout.addWidget(QtGui.QLabel("Type:"))
        specify_version_groupbox_layout.addWidget(self.type_combobox)
        specify_version_groupbox_layout.addWidget(QtGui.QLabel("Name:"))
        specify_version_groupbox_layout.addWidget(self.id_combobox)
        specify_version_groupbox_layout.addStretch()
        specify_version_groupbox.setLayout(specify_version_groupbox_layout)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(notes_groupbox)
        main_layout.addWidget(specify_version_groupbox)
        self.setLayout(main_layout)

    def _type_changed(self, text):
        pass

    def _id_changed(self, text):
        pass

    def get_name(self):
        return self.ProfileInstance.get_name()

    def close(self):
        super(ProfileInstanceTab, self).close()

class VersionsManagerTab(QtGui.QWidget):
    def __init__(self, launcher_obj, parent=None):
        super(VersionsManagerTab, self).__init__(parent)
        self.Launcher = launcher_obj

class LibrariesManagerTab(QtGui.QWidget):
    def __init__(self, launcher_obj, parent=None):
        super(LibrariesManagerTab, self).__init__(parent)
        self.Launcher = launcher_obj

class MainGUI(QtGui.QMainWindow):
    def __init__(self, launcher_obj):
        super(MainGUI, self).__init__()
        self.Launcher = launcher_obj

        MainTabs = QtGui.QTabWidget()
        MainTabs.addTab(AccountTab(self.Launcher), "Account")
        MainTabs.addTab(ProfilesTab(self.Launcher), "Profiles")

        self.add_menus()
        self.setCentralWidget(MainTabs)
        self.statusBar().showMessage("Welcome to YAMCL!")
        self.setWindowTitle("YAMCL")

    def shutdown(self):
        self.Launcher.shutdown()
        self.close()

    def open_data_path(self):
        '''
        Opens the YAMCL profile directory in the system's file explorer
        '''
        current_platform = self.Launcher.PlatformTools.get_os_family()
        yamcl_data_path = str(self.Launcher.ROOT_PATH)
        if current_platform == "windows":
            os.startfile(yamcl_data_path)

        elif current_platform == "osx":
            subprocess.Popen(['open', yamcl_data_path])

        else:
            subprocess.Popen(['xdg-open', yamcl_data_path])

    def add_menus(self):
        self.yamcl_menu = self.menuBar().addMenu("&YAMCL")
        data_path_action = QtGui.QAction("&Open Data Path", self, statusTip="Opens the YAMCL data directory in a file browser", triggered=self.open_data_path)
        exit_action = QtGui.QAction("&Exit", self, statusTip="Safely shutdown YAMCL", triggered=self.shutdown)
        self.yamcl_menu.addAction(data_path_action)
        self.yamcl_menu.addAction(exit_action)
