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

from graphical_interface import NotesEditor, ConsoleOutput

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
        self.offline_username.setText(self.Launcher.AccountManager.get_account().get_game_username())
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
            if self.Launcher.AccountManager.get_account().is_authenticated():
                clicked_button = QtGui.QMessageBox.question(self, "YAMCL: Sign-out?", "You are currently signed-in. YAMCL must sign you out first before switching offline. Do you want to continue?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if clicked_button == QtGui.QMessageBox.Yes:
                    self._signout()
                else:
                    self.online_radio.setChecked(True)
                    return
            self.Launcher.AccountManager.switch_offline()
            self.offline_settings_groupbox.setEnabled(True)
            self.online_settings_groupbox.setEnabled(False)
        elif self.online_radio.isChecked():
            self.Launcher.AccountManager.switch_online()
            self.offline_settings_groupbox.setEnabled(False)
            self.online_settings_groupbox.setEnabled(True)

    def _set_offline_username(self):
        self.Launcher.AccountManager.get_account().set_game_username(self.offline_username.text())
        QtGui.QMessageBox.information(self, "YAMCL: Changed Offline Username", "The username is now: " + self.offline_username.text())

    def _signin(self):
        self.Launcher.AccountManager.get_account().set_account_username(self.online_username.text())
        success, error_title, error_message = self.Launcher.AccountManager.get_account().authenticate(self.online_password.text())
        self.online_password.setText(str())
        if success:
            self.online_username.setEnabled(False)
            self.online_password.setEnabled(False)
            self.signin_button.setEnabled(False)
            self.signout_button.setEnabled(True)
        else:
            QtGui.QMessageBox.critical(self, "Sign-in Error: " + error_title, error_message, QtGui.QMessageBox.Ok)

    def _signout(self):
        success, error_title, error_message = self.Launcher.AccountManager.get_account().invalidate()
        self.online_username.setEnabled(True)
        self.online_password.setEnabled(True)
        self.signin_button.setEnabled(True)
        self.signout_button.setEnabled(False)
        if not success:
            QtGui.QMessageBox.critical(self, "Sign-out Error: " + error_title, error_message, QtGui.QMessageBox.Ok)

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
        new_profile_button.clicked.connect(self._new_profile)
        delete_profile_button = QtGui.QPushButton("Delete Profile")
        delete_profile_button.clicked.connect(self._delete_profile)
        rename_profile_button = QtGui.QPushButton("Rename Profile")
        rename_profile_button.clicked.connect(self._rename_profile)
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

    def _get_unopened_profiles(self):
        unopened_profile_list = list()
        all_profiles = self.Launcher.ProfileManager.get_profile_list()
        if len(all_profiles) == 0:
            return 1
        for current_profile in all_profiles:
            if not current_profile in self.open_profile_instances:
                unopened_profile_list.append(current_profile)
        if len(unopened_profile_list) == 0:
            return 2
        return unopened_profile_list

    def _open_profile_tab(self):
        unopened_profile_list = self._get_unopened_profiles()
        if unopened_profile_list == 1:
            QtGui.QMessageBox.critical(self, "YAMCL: Open Profile Error", "You have not created any profiles.", QtGui.QMessageBox.Ok)
            return
        elif unopened_profile_list == 2:
            QtGui.QMessageBox.critical(self, "YAMCL: Open Profile Error", "There are no more profiles left to open.", QtGui.QMessageBox.Ok)
            return
        profile_name, success = QtGui.QInputDialog.getItem(self, "YAMCL: Open Profile", "Specify a Profile:", unopened_profile_list, 0, False) # Tuple unpacking
        if success:
            tmp_profile_instance = self.Launcher.ProfileManager.get_profile_instance(profile_name)
            tmp_profile_tab = ProfileInstanceTab(self.Launcher, tmp_profile_instance)
            self.open_profile_instances.append(profile_name)
            self.profile_instance_tabwidget.addTab(tmp_profile_tab, profile_name)

    def _delete_profile(self):
        unopened_profile_list = self._get_unopened_profiles()
        if unopened_profile_list == 1:
            QtGui.QMessageBox.critical(self, "YAMCL: Delete Profile Error", "You have not created any profiles.", QtGui.QMessageBox.Ok)
            return
        elif unopened_profile_list == 2:
            QtGui.QMessageBox.critical(self, "YAMCL: Delete Profile Error", "All profiles are open. You can only delete closed profiles.", QtGui.QMessageBox.Ok)
            return
        profile_name, success = QtGui.QInputDialog.getItem(self, "YAMCL: Delete Profile", "Specify an unopened profile to delete:", unopened_profile_list, 0, False)
        if success:
            if profile_name in self.open_profile_instances:
                QtGui.QMessageBox.critical(self, "YAMCL: Delete Profile Error", "Profile " + profile_name + " is open. Please close it first to delete it.", QtGui.QMessageBox.Ok)
            else:
                clicked_button = QtGui.QMessageBox.question(self, "YAMCL: Confirm Delete", "Are you sure you want to delete profile '" + profile_name + "'?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                if clicked_button == QtGui.QMessageBox.Yes:
                    self.Launcher.ProfileManager.delete(profile_name)

    def _rename_profile(self):
        unopened_profile_list = self._get_unopened_profiles()
        if unopened_profile_list == 1:
            QtGui.QMessageBox.critical(self, "YAMCL: Rename Profile Error", "You have not created any profiles.", QtGui.QMessageBox.Ok)
            return
        elif unopened_profile_list == 2:
            QtGui.QMessageBox.critical(self, "YAMCL: Rename Profile Error", "All profiles are open. You can only rename closed profiles.", QtGui.QMessageBox.Ok)
            return
        profile_name, select_success = QtGui.QInputDialog.getItem(self, "YAMCL: Rename Profile", "Specify an unopened profile to rename:", unopened_profile_list, 0, False)
        if select_success:
            input_success = True
            last_name = str()
            while input_success:
                new_profile_name, input_success = QtGui.QInputDialog.getText(self, "YAMCL: New Profile", "Specify a new profile name", QtGui.QLineEdit.Normal, last_name)
                if input_success:
                    if not len(new_profile_name) > 0:
                        QtGui.QMessageBox.critical(self, "YAMCL: Rename Profile Name Blank", "The new profile name cannot be blank. Please specify a name.", QtGui.QMessageBox.Ok)
                        continue
                    if new_profile_name in self.Launcher.ProfileManager.get_profile_list():
                        QtGui.QMessageBox.critical(self, "YAMCL: Rename Profile Name Conflict", "Profile name '" + new_profile_name + "' already exists.", QtGui.QMessageBox.Ok)
                        last_name = new_profile_name
                    else:
                        self.Launcher.ProfileManager.rename(profile_name, new_profile_name)
                        break

    def _close_tab(self, index):
        profile_tab = self.profile_instance_tabwidget.widget(index)
        self.open_profile_instances.remove(profile_tab.get_name())
        profile_tab.close()
        self.profile_instance_tabwidget.removeTab(index)

    def _new_profile(self):
        success = True
        last_name = str()
        while success:
            text, success = QtGui.QInputDialog.getText(self, "YAMCL: New Profile", "Specify a new profile name", QtGui.QLineEdit.Normal, last_name)
            if success:
                if not len(text) > 0:
                    QtGui.QMessageBox.critical(self, "YAMCL: Profile Name Blank", "The profile name cannot be blank. Please specify a name.", QtGui.QMessageBox.Ok)
                    continue
                if text in self.Launcher.ProfileManager.get_profile_list():
                    QtGui.QMessageBox.critical(self, "YAMCL: Profile Name Conflict", "Profile name '" + text + "' already exists.", QtGui.QMessageBox.Ok)
                    last_name = text
                else:
                    self.Launcher.ProfileManager.new(text)
                    break

class ProfileInstanceTab(QtGui.QWidget):
    def __init__(self, launcher_obj, instance_obj, parent=None):
        super(ProfileInstanceTab, self).__init__(parent)
        self.Launcher = launcher_obj
        self.ProfileInstance = instance_obj

        self.notes_editor = None
        self.console_output = None

        notes_groupbox = QtGui.QGroupBox("Notes")
        self.notes_preview = QtGui.QTextBrowser()
        self.notes_preview.setPlainText(self.ProfileInstance.get_notes())
        edit_notes_button = QtGui.QPushButton("Edit Notes")
        edit_notes_button.clicked.connect(self._open_notes_editor)
        notes_groupbox_layout = QtGui.QHBoxLayout()
        notes_groupbox_layout.addWidget(self.notes_preview)
        notes_groupbox_layout.addWidget(edit_notes_button)
        notes_groupbox.setLayout(notes_groupbox_layout)

        specify_version_groupbox = QtGui.QGroupBox("Version to Launch")
        self.type_combobox = QtGui.QComboBox()
        self.type_combobox.addItems(["custom", "vanilla"])
        self.type_combobox.currentIndexChanged[str].connect(self._type_changed)
        self.id_combobox = QtGui.QComboBox()
        self.id_combobox.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents) # Combobox will resize to always fit its contents
        #self.id_combobox.currentIndexChanged[str].connect(self._id_changed)
        refresh_ids_button = QtGui.QPushButton("Refresh Names")
        refresh_ids_button.clicked.connect(self._manual_ids_refresh)
        specify_version_groupbox_layout = QtGui.QHBoxLayout()
        specify_version_groupbox_layout.addWidget(QtGui.QLabel("Type:"))
        specify_version_groupbox_layout.addWidget(self.type_combobox)
        specify_version_groupbox_layout.addWidget(QtGui.QLabel("Name:"))
        specify_version_groupbox_layout.addWidget(self.id_combobox)
        specify_version_groupbox_layout.addWidget(refresh_ids_button)
        specify_version_groupbox_layout.addStretch()
        specify_version_groupbox.setLayout(specify_version_groupbox_layout)

        open_profile_button = QtGui.QPushButton("Open Profile Directory")
        open_profile_button.clicked.connect(self._open_profile_path)
        launch_game_button = QtGui.QPushButton("Launch Game")
        launch_game_button.clicked.connect(self._launch_game)
        show_game_output_button = QtGui.QPushButton("Show Game Output")
        show_game_output_button.clicked.connect(self._open_game_output)
        action_buttons_layout = QtGui.QHBoxLayout()
        action_buttons_layout.addWidget(open_profile_button)
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(launch_game_button)
        action_buttons_layout.addStretch()
        action_buttons_layout.addWidget(show_game_output_button)

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(notes_groupbox)
        main_layout.addWidget(specify_version_groupbox)
        main_layout.addLayout(action_buttons_layout)
        self.setLayout(main_layout)

        self.type_combobox.setCurrentIndex(self.type_combobox.findText(self.ProfileInstance.get_last_version()["type"]))
        if len(self.type_combobox.currentText()) > 0:
            self.update_id_list(self.Launcher.BinaryManager.get_installed_versions()[self.type_combobox.currentText()])
            self.id_combobox.setCurrentIndex(self.id_combobox.findText(self.ProfileInstance.get_last_version()["id"]))

    def _selected_id(self):
        tmp_text = self.id_combobox.currentText()
        if len(tmp_text) == 0:
            return None
        else:
            return tmp_text

    def _selected_type(self):
        tmp_text = self.type_combobox.currentText()
        if len(tmp_text) == 0:
            return None
        else:
            return tmp_text

    def _manual_ids_refresh(self):
        if not self._selected_type() == None:
            self.update_id_list(self.Launcher.BinaryManager.get_installed_versions()[self._selected_type()])

    def _type_changed(self, text):
        if not len(text) == 0:
            self.current_type = text
            self.update_id_list(self.Launcher.BinaryManager.get_installed_versions()[text])

    def _open_profile_path(self):
        current_platform = self.Launcher.PlatformTools.get_os_family()
        if current_platform == "windows":
            os.startfile(str(self.ProfileInstance.get_path()))

        elif current_platform == "osx":
            subprocess.Popen(['open', str(self.ProfileInstance.get_path())])

        else:
            subprocess.Popen(['xdg-open', str(self.ProfileInstance.get_path())])

    def _launch_game(self):
        if self._selected_id() == None or self._selected_type() == None:
            QtGui.QMessageBox.critical(self, "YAMCL: Game Launch Error", "A version type or name has not been specified. Please select them before launching.", QtGui.QMessageBox.Ok)
            return
        if self.ProfileInstance.check_game_running():
            QtGui.QMessageBox.critical(self, "YAMCL: Game Launch Error", "An instance of Minecraft is already running on this profile. Please close Minecraft first before launching again.", QtGui.QMessageBox.Ok)
            return
        self.ProfileInstance.set_last_version(self._selected_id(), self._selected_type())
        self.ProfileInstance.launch_version(self._selected_id(), self._selected_type())
        self.console_output = ConsoleOutput.GameOutput(self.ProfileInstance.get_name(), self.ProfileInstance.get_output_object())

    def _open_notes_editor(self):
        self.notes_editor = NotesEditor.NotesEditor(self.ProfileInstance.get_name(), self.ProfileInstance.get_notes(), self.set_new_notes)
        self.notes_editor.show()

    def _open_game_output(self):
        if self.ProfileInstance.check_game_running():
            self.console_output.show()
        else:
            QtGui.QMessageBox.critical(self, "YAMCL: Game Output Error", "You must start Minecraft first before opening the output window.", QtGui.QMessageBox.Ok)

    def update_id_list(self, id_list):
        self.id_combobox.clear()
        self.id_combobox.addItems(id_list)

    def get_name(self):
        return self.ProfileInstance.get_name()

    def set_new_notes(self, notes_content):
        self.notes_preview.setPlainText(notes_content)
        self.ProfileInstance.set_notes(notes_content)

    def close(self):
        self.Launcher.ProfileManager.delete_profile_instance(self.ProfileInstance.get_name())
        super(ProfileInstanceTab, self).close()

class ProgressDialogEvents(QtCore.QObject):
    set_label_sig = QtCore.Signal(str)
    set_range_sig = QtCore.Signal(int, int)
    set_value_sig = QtCore.Signal(int)
    show_dialog_sig = QtCore.Signal()
    close_dialog_sig = QtCore.Signal()
    window_title = QtCore.Signal(str)

    def __init__(self):
        QtCore.QObject.__init__(self)

    def set_label(self, text):
        self.set_label_sig.emit(text)
        QtGui.QApplication.processEvents()

    def status_update(self, label, value):
        self.set_label_sig.emit(label)
        self.set_value_sig.emit(round(value*100.0))
        QtGui.QApplication.processEvents()

    def show_dialog(self):
        self.show_dialog_sig.emit()
        QtGui.QApplication.processEvents()

    def set_range(self, minval, maxval):
        self.set_range_sig.emit(minval, maxval)
        QtGui.QApplication.processEvents()

    def close_dialog(self):
        self.close_dialog_sig.emit()
        QtGui.QApplication.processEvents()

    def set_window_title(self, text):
        self.window_title.emit(text)
        QtGui.QApplication.processEvents()

class VersionsManagerTab(QtGui.QWidget):
    def __init__(self, launcher_obj, parent=None):
        super(VersionsManagerTab, self).__init__(parent)
        self.Launcher = launcher_obj

        official_versions_groupbox = QtGui.QGroupBox("Download Official Versions")
        index_refresh_button = QtGui.QPushButton("Download List")
        index_refresh_button.clicked.connect(self._download_list)
        self.install_selected_button = QtGui.QPushButton("Install Selected")
        self.install_selected_button.clicked.connect(self._install_selected)
        self.install_selected_button.setEnabled(False)
        self.official_versions_model = QtGui.QStandardItemModel()
        self.official_versions_model.setHorizontalHeaderLabels(["Click 'Download List' to populate"])
        self.official_versions_treeview = QtGui.QTreeView()
        self.official_versions_treeview.setModel(self.official_versions_model)
        self.official_versions_treeview.setSelectionModel(QtGui.QItemSelectionModel(self.official_versions_model))
        self.official_versions_treeview.selectionModel().currentChanged.connect(self._official_versions_item_change)
        official_versions_buttonlayout = QtGui.QVBoxLayout()
        official_versions_buttonlayout.addWidget(index_refresh_button)
        official_versions_buttonlayout.addStretch()
        official_versions_buttonlayout.addWidget(QtGui.QLabel("Latest Release:"))
        self.latest_release_label = QtGui.QLabel("Unknown")
        official_versions_buttonlayout.addWidget(self.latest_release_label)
        official_versions_buttonlayout.addWidget(QtGui.QLabel("Latest Snapshot:"))
        self.latest_snapshot_label = QtGui.QLabel("Unknown")
        official_versions_buttonlayout.addWidget(self.latest_snapshot_label)
        official_versions_buttonlayout.addStretch()
        official_versions_buttonlayout.addWidget(self.install_selected_button)
        official_versions_layout = QtGui.QHBoxLayout()
        official_versions_layout.addWidget(self.official_versions_treeview)
        official_versions_layout.addLayout(official_versions_buttonlayout)
        official_versions_groupbox.setLayout(official_versions_layout)

        manage_versions_groupbox = QtGui.QGroupBox("Manage Versions")
        self.manage_versions_treeview = QtGui.QTreeView()
        self.edit_notes_button = QtGui.QPushButton("Edit Notes")
        self.edit_notes_button.setEnabled(False)
        self.open_directory_button = QtGui.QPushButton("Open Directory")
        self.open_directory_button.setEnabled(False)
        self.rename_button = QtGui.QPushButton("Rename")
        self.rename_button.setEnabled(False)
        self.delete_button = QtGui.QPushButton("Delete")
        self.delete_button.setEnabled(False)
        manage_versions_buttonlayout = QtGui.QVBoxLayout()
        manage_versions_buttonlayout.addWidget(QtGui.QLabel("Selected Version:"))
        manage_versions_buttonlayout.addWidget(self.edit_notes_button)
        manage_versions_buttonlayout.addWidget(self.open_directory_button)
        manage_versions_buttonlayout.addWidget(self.rename_button)
        manage_versions_buttonlayout.addWidget(self.delete_button)
        manage_versions_buttonlayout.addStretch()
        manage_versions_layout = QtGui.QHBoxLayout()
        manage_versions_layout.addWidget(self.manage_versions_treeview)
        manage_versions_layout.addLayout(manage_versions_buttonlayout)
        manage_versions_groupbox.setLayout(manage_versions_layout)

        local_storage_button = QtGui.QPushButton("Local Storage")
        existing_official_button = QtGui.QPushButton("Existing Official Version")
        install_buttonlayout = QtGui.QHBoxLayout()
        install_buttonlayout.addWidget(QtGui.QLabel("Install custom version from:"))
        install_buttonlayout.addWidget(local_storage_button)
        install_buttonlayout.addWidget(existing_official_button)
        install_buttonlayout.addStretch()

        main_layout = QtGui.QVBoxLayout()
        main_layout.addWidget(official_versions_groupbox)
        main_layout.addWidget(manage_versions_groupbox)
        main_layout.addLayout(install_buttonlayout)
        self.setLayout(main_layout)

        self.progress_dialog_events = ProgressDialogEvents()
        self.progress_dialog = QtGui.QProgressDialog()
        self.progress_dialog_events.set_label_sig.connect(self.progress_dialog.setLabelText, type=QtCore.Qt.QueuedConnection)
        self.progress_dialog_events.set_range_sig.connect(self.progress_dialog.setRange, type=QtCore.Qt.QueuedConnection)
        self.progress_dialog_events.set_value_sig.connect(self.progress_dialog.setValue, type=QtCore.Qt.QueuedConnection)
        self.progress_dialog_events.show_dialog_sig.connect(self.progress_dialog.show, type=QtCore.Qt.QueuedConnection)
        self.progress_dialog_events.close_dialog_sig.connect(self.progress_dialog.close, type=QtCore.Qt.QueuedConnection)
        self.progress_dialog_events.window_title.connect(self.progress_dialog.setWindowTitle, type=QtCore.Qt.QueuedConnection)
        self.progress_dialog_events.set_range(0, 100)
        self.progress_dialog.setAutoClose(False)

    def _populate_official_versions_treeview(self):
        self.install_selected_button.setEnabled(False)
        data = self.Launcher.VersionsListManager.get_versions()
        version_type_dict = dict()
        for current_version in data["versions"]:
            if not self.Launcher.BinaryManager.version_exists(current_version["id"], "vanilla"):
                if not current_version["type"] in version_type_dict:
                    type_item = QtGui.QStandardItem(current_version["type"])
                    type_item.setFlags(QtCore.Qt.ItemIsEnabled)
                    version_type_dict[current_version["type"]] = type_item
                version_item = QtGui.QStandardItem(current_version["id"])
                version_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                version_type_dict[current_version["type"]].appendRow(version_item)
        self.official_versions_model.clear()
        self.official_versions_model.setHorizontalHeaderLabels(["Official Versions Available"])
        root_item = self.official_versions_model.invisibleRootItem()
        for item_type in version_type_dict:
            root_item.appendRow(version_type_dict[item_type])

    def _load_official_versions(self):
        self._populate_official_versions_treeview()
        self.latest_release_label.setText(self.Launcher.VersionsListManager.get_latest_release())
        self.latest_snapshot_label.setText(self.Launcher.VersionsListManager.get_latest_snapshot())

    def _download_list(self):
        first_time = self.Launcher.VersionsListManager.get_versions() == None
        self.Launcher.VersionsListManager.download_versions()
        self._load_official_versions()
        if not first_time:
            QtGui.QMessageBox.information(self, "YAMCL: Download Available Versions Index", "The latest versions index has been downloaded.")

    def _official_versions_item_change(self, index, previous):
        self.install_selected_button.setEnabled(not self.official_versions_model.itemFromIndex(index).hasChildren())

    def _install_selected(self):
        vanilla_id = self.official_versions_model.itemFromIndex(self.official_versions_treeview.currentIndex()).text()
        clicked_button = QtGui.QMessageBox.question(self, "YAMCL: Install " + vanilla_id + "?", "You have chosen to install: " + vanilla_id + "\nAre you sure you want to continue?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if clicked_button == QtGui.QMessageBox.Yes:
            self.progress_dialog_events.set_window_title("Downloading " + vanilla_id)
            self.progress_dialog_events.status_update("Downloading binary", 0.5)
            self.progress_dialog_events.show_dialog()
            self.Launcher.BinaryManager.download_official(vanilla_id)
            self.progress_dialog_events.status_update("Downloading binary", 1.0)
            binary_parser = self.Launcher.BinaryManager.get_binary_parser(vanilla_id, "vanilla")
            self.Launcher.LibraryManager.download_missing(binary_parser.get_library_parsers(), self.progress_dialog_events.status_update)
            self.Launcher.AssetsManager.download_index(binary_parser.get_assets_id())
            self.Launcher.AssetsManager.download_missing(binary_parser.get_assets_id(), self.progress_dialog_events.status_update)
            self.progress_dialog_events.close_dialog()
            self._load_official_versions()
            QtGui.QMessageBox.information(self, "YAMCL: Installed " + vanilla_id, "Official version " + vanilla_id + " installed successfully")

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
        MainTabs.addTab(VersionsManagerTab(self.Launcher), "Versions Manager")

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
