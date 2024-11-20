import requests
from requests.packages import urllib3
import ssl
import os
import json
# import time
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AAA_API():

    def __init__(self, username, password, environment='prod'):

        self.username = username
        self.password = password

        self.domain = "https://www.eodms-sgdot.nrcan-rncan.gc.ca"

        self.access_token = None
        self.refresh_token = None

        pkg_folder = os.path.dirname(os.path.dirname(__file__))
        self.auth_folder = os.path.join(pkg_folder, 'auth')

        if not os.path.exists(self.auth_folder):
            os.mkdir(self.auth_folder)

    def login(self):

        url = f"{self.domain}/aaa/v1/login"

        print(f"login url: {url}")
        
        payload = {
            "grant_type": "password",
            "password": self.password,
            "username": self.username
        }

        # print(f"payload: {payload}")

        resp = requests.post(url, json=payload, verify=False) #, verify=False)

        auth_fn = os.path.join(self.auth_folder, 'auth.json')

        if resp.status_code == 200:
            print("\nSuccessfully logged in using AAA API")
            login_json = resp.json()
            self.access_token = login_json.get('access_token')
            self.refresh_token = login_json.get('refresh_token')

            # login_json["login_timestamp"] = datetime.now()

            # Store the tokens
            with open(auth_fn, 'w') as f:
                json.dump(login_json, f)
        elif resp.status_code == 429:
            if os.path.exists(auth_fn):
                with open(auth_fn, 'r') as file:
                    data = json.load(file)
                
                self.access_token = data.get('access_token')
                self.refresh_token = data.get('refresh_token')

                self.refresh()
            else:
                print("\nFailed to log in using AAA API")
                err_json = resp.json()
                error = err_json.get('error')
                msg = err_json.get('message')
                print(f"{error}: {msg}")
        else:
            print("\nFailed to log in using AAA API")
            err_json = resp.json()
            error = err_json.get('error')
            msg = err_json.get('message')
            print(f"{error}: {msg}")

        return resp.json()
    
    def refresh(self):
        url = f"{self.}/aaa/v1/refresh"

        print(f"refresh url: {url}")

        resp = requests.get(url, verify=False)

        if self.refresh_token is None:
            login_info = self.login()
            return login_info

        headers = {"Authorization": f"Bearer {self.refresh_token}"}
        resp = requests.get(url, headers=headers, verify=False)

        if resp.status_code == 200:
            print("\nSuccessfully refreshed using AAA API")
            ref_json = resp.json()
            self.access_token = ref_json.get('access_token')
        else:
            print("\nFailed to refresh using AAA API")
            err_json = resp.json()
            error = err_json.get('error')
            msg = err_json.get('message')
            print(f"{error}: {msg}")

        return resp.json()

        
