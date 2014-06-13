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

import urllib.error
import uuid

from yamcl.globals import URL
from yamcl.tools import JSONTools

class GeneralAccount:
    def __init__(self):
        self.game_username = "Player"
        self.account_username = "Player"
        self.uuid = "00000000-0000-0000-0000-000000000000"
        self.access_token = None
        self.user_type = "legacy"
        self.user_properties = str(dict()) # Unused?
        self.session_id = "-" # This is deprecated in the Yggdrasil authentication system

    def get_game_username(self):
        return self.game_username

    def get_account_username(self):
        return self.account_username

    def get_uuid(self):
        return self.uuid

    def get_access_token(self):
        return self.access_token

    def get_user_type(self):
        return self.user_type

    def get_user_properties(self):
        return self.user_properties

    def get_session(self):
        return self.session_id

class OfflineAccount(GeneralAccount):
    def __init__(self):
        super(OfflineAccount, self).__init__()
        self.access_token = "0"

    def set_game_username(self, new_username):
        self.game_username = new_username

class OnlineAccount(GeneralAccount):
    TEXT_ENCODING = "UTF-8"
    def __init__(self):
        super(OnlineAccount, self).__init__()
        self.client_token = uuid.uuid4().hex
        self.signedin = False

    def set_account_username(self, username):
        self.account_username = username

    def is_authenticated(self):
        return self.signedin

    def _communicate(self, endpoint, payload):
        '''
        Endpoint is a string path
        Payload is a JSON object
        '''
        headers = dict()
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = "YAMCL"
        url_obj = URL(endpoint, URL.AUTH)
        server_data = [None, None]
        try:
            url_request = url_obj.url_object(JSONTools.serialize_json(payload).encode(OnlineAccount.TEXT_ENCODING), headers)
            server_data[0] = True
            try:
                server_data[1] = JSONTools.read_json(url_request.read().decode(OnlineAccount.TEXT_ENCODING))
            except ValueError:
                server_data[1] = None
        except urllib.error.HTTPError as http_error:
            server_data[0] = False
            try:
                server_data[1] = JSONTools.read_json(http_error.read().decode(OnlineAccount.TEXT_ENCODING))
            except ValueError:
                server_data[1] = None
        return server_data

    def authenticate(self, pw):
        '''
        Gets an access token, uuid, and account type with a username and password
        NOTE: access tokens do not seem to expire for a long time
        '''
        post_payload = dict()
        post_payload["agent"] = {"name": "Minecraft", "version": 1}
        post_payload["username"] = self.account_username
        post_payload["password"] = pw
        post_payload["clientToken"] = self.client_token
        success, server_data = self._communicate("authenticate", post_payload)
        status_data = [success, "", ""]
        if success:
            if server_data["clientToken"] == self.client_token:
                self.signedin = True
                self.access_token = server_data["accessToken"]
                self.uuid = server_data["selectedProfile"]["id"]
                self.game_username = server_data["selectedProfile"]["name"]
                self.user_type = "mojang"
                if "legacy" in server_data["selectedProfile"]:
                    if server_data["selectedProfile"]["legacy"]:
                        self.user_type = "legacy"
            else:
                status_data[0] = False
                status_data[1] = "Authentication Error"
                status_data[2] = "Received client token does not match"
        else:
            status_data[1] = server_data["error"]
            status_data[2] = server_data["errorMessage"]
        return status_data

    def refresh(self):
        '''
        Generates a new access token from an old access token. Invalidates the old access token
        '''
        if self.access_token == None:
            raise Exception("There was no pre-existing access token")
        post_payload = dict()
        post_payload["accessToken"] = self.access_token
        post_payload["clientToken"] = self.client_token
        success, server_data = self._communicate("refresh", post_payload)
        status_data = [success, "", ""]
        if success:
            if server_data["clientToken"] == self.client_token:
                self.access_token = server_data["accessToken"]
            else:
                status_data[0] = False
                status_data[1] = "Authentication Error"
                status_data[2] = "Received client token does not match"
        else:
            status_data[1] = server_data["error"]
            status_data[2] = server_data["errorMessage"]
        return status_data

    def validate(self):
        '''
        Returns True if the access token is valid, otherwise False
        '''
        post_payload = dict()
        post_payload["accessToken"] = self.access_token
        success, server_data = self._communicate("validate", post_payload)
        return success

    def invalidate(self):
        '''
        Invalidates the access token and ends the session, essentially logging out
        This is equivalent to signout but without the need to store a password
        '''
        post_payload = dict()
        post_payload["accessToken"] = self.access_token
        post_payload["clientToken"] = self.client_token
        success, server_data = self._communicate("invalidate", post_payload)
        status_data = [success, "", ""]
        if not success:
            status_data[1] = server_data["error"]
            status_data[2] = server_data["errorMessage"]
        self.signedin = False
        self.access_token = None # Perhaps there is a situation where the access token is still valid but the invalidate function failed?
        return status_data

    def signout(self, pw):
        '''
        Invalidates the access token and ends the session, essentially logging out
        This is equivalent to invalidate but using a password
        '''
        post_payload = dict()
        post_payload["username"] = self.account_username
        post_payload["password"] = pw
        success, server_data = self._communicate("signout", post_payload)
        status_data = [success, "", ""]
        if not success:
            status_data[1] = server_data["error"]
            status_data[2] = server_data["errorMessage"]
        self.signedin = False
        self.access_token = None # Same issue as invalidate
        return status_data

class AccountManager:
    def __init__(self):
        self.account_obj = OfflineAccount()

    def is_offline(self):
        return isinstance(self.account_obj, OfflineAccount)

    def get_account(self):
        return self.account_obj

    def switch_offline(self):
        if self.is_offline():
            return
        self.account_obj = OfflineAccount()

    def switch_online(self):
        if not self.is_offline():
            return
        self.account_obj = OnlineAccount()

    def shutdown(self):
        if not self.is_offline():
            if self.account_obj.is_authenticated():
                self.account_obj.invalidate()
