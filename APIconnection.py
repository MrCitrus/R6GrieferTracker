import base64
import requests
import json

class InvalidPlayer(Exception):
    def __init__(self, *args, code = 0, **kwargs):
        super().__init__(*args, **kwargs)
        self.code = code

class API_connection:
    ubi_email = None
    ubi_password = None
    login_credentials_changed = False
    app_id = "39baebad-39e5-4552-8c25-2c9b919064e2"
    def __init__(self):
        self.session = requests.session()
        self.session_id = None
        self.ticket = None
        self.logged_in = False
        self.reauth_date = None
    @classmethod
    def validate_log_in_details(cls, Ubi_email, Ubi_Password):
        auth_token = API_connection.get_authentication_token(Ubi_email, Ubi_Password)
        response =  requests.post("https://connect.ubi.com/ubiservices/v2/profiles/sessions", headers = {
                "Content-Type": "application/json",
                "Ubi-AppId": API_connection.app_id,
                "Authorization": "Basic " + auth_token,
                "Connection" : "keep-alive"

            })
        json_data = response.json()
        if "ticket" in json_data:
            API_connection.ubi_email = Ubi_email
            API_connection.ubi_password = Ubi_Password
            API_connection.login_credentials_changed = True
            return True
        else:
            API_connection.ubi_email = None
            API_connection.ubi_password = None
            return False
    @classmethod
    def get_authentication_token(cls, Ubi_email, Ubi_password):
        return base64.b64encode((Ubi_email + ":" + Ubi_password).encode("utf-8")).decode("utf-8")
    def authenticate(self):
        print("---------------------authenticating-----------------")
        self.auth_token = API_connection.get_authentication_token(API_connection.ubi_email, API_connection.ubi_password)
        self.response =  self.session.post("https://connect.ubi.com/ubiservices/v2/profiles/sessions", headers = {
                "Content-Type": "application/json",
                "Ubi-AppId": API_connection.app_id,
                "Authorization": "Basic " + self.auth_token,
                "Connection" : "keep-alive"

            })
        self.json_data = self.response.json()
        print(self.json_data)

        self.session_id = self.json_data.get("sessionId")
        self.ticket = self.json_data.get("ticket")
        self.logged_in = True

    def get_uuid_from_username(self,username):
        self.base_url = "https://public-ubiservices.ubi.com/v2/profiles?nameOnPlatform={}&platformType={}".format(username, "uplay")
        self.response= self.session.get(self.base_url, headers = {"Ubi-AppId": API_connection.app_id, "Authorization": "Ubi_v1 t=" + self.ticket})
        self.data = self.response.json()
        print(self.data)
        if (len(self.data['profiles']) == 0): raise InvalidPlayer()
        print(self.data)
        return self.data['profiles'][0]['profileId']
    def get_list_uuids_from_usernames(self, usernames):
        username_list = [] #list of (username,uuid) tuples

        print("here is the list: ", usernames)
        for username in usernames:
            if username != "":
                self.base_url = "https://public-ubiservices.ubi.com/v2/profiles?nameOnPlatform={}&platformType={}".format(username, "uplay")
                self.response= self.session.get(self.base_url, headers = {"Ubi-AppId": API_connection.app_id, "Authorization": "Ubi_v1 t=" + self.ticket})
                self.data = self.response.json()
                print("json response: ", self.data)
                if (len(self.data['profiles']) == 0): continue
                username_list.append((username, self.data['profiles'][0]['profileId']))
        print(username_list)
        return username_list
