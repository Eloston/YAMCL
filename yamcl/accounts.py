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
        self.access_token = "0"
        self.user_type = "legacy"
        self.user_properties = str(dict())
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

    def set_game_username(self, new_username):
        self.game_username = new_username

class OnlineAccount(GeneralAccount):
    TEXT_ENCODING = "UTF-8"
    def __init__(self):
        super(OnlineAccount, self).__init__()
        self.password = None
        self.client_token = uuid.uuid4().hex

    def _communicate(self, endpoint, payload):
        '''
        Endpoint is a string path
        Payload is a JSON object
        '''
        # NOTE: https://docs.python.org/3.4/howto/urllib2.html
        # TODO: Generate random 32 character clientToken?
        headers = dict()
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = "YAMCL"
        url_obj = URL(endpoint, URL.AUTH)
        server_data = list()
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

    def authenticate(self, username, pw):
        post_payload = dict()
        post_payload["agent"] = {"name": "Minecraft", "version": 1}
        post_payload["username"] = username
        post_payload["password"] = pw
        post_payload["clientToken"] = self.client_token
        success, server_data = self._communicate("authenticate", post_payload)
        if success:
            if not server_data["clientToken"] == self.client_token:
                raise Exception("Client Tokens are not the same") # TODO: Change this
            self.access_token = server_data["accessToken"]
            self.user_type = "mojang"
            if "legacy" in server_data["availableProfiles"]:
                if server_data["availableProfiles"]["legacy"]:
                    self.user_type = "legacy"
    def refresh():
        pass
    def validate():
        pass
    def signout():
        pass

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
            self.account_obj.signout()
