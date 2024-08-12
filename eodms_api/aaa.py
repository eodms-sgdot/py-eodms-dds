import requests
from requests.packages import urllib3
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AAA_API():

    def __init__(self):
        self.domain = "https://www-staging-eodms.aws.nrcan-rncan.cloud"

        self.access_token = None
        self.refresh_token = None

    def login(self, username, password):

        url = f"{self.domain}/aaa/v1/login"

        print(f"login url: {url}")
        
        payload = {
            "grant_type": "password",
            "password": password,
            "username": username
        }

        # print(f"payload: {payload}")

        resp = requests.post(url, json=payload, verify=False) #, verify=False)

        if resp.status_code == 200:
            print("\nSuccessfully logged in using AAA API")
            login_json = resp.json()
            self.access_token = login_json.get('access_token')
            self.refresh_token = login_json.get('refresh_token')
        else:
            print("\nFailed to log in using AAA API")
            err_json = resp.json()
            error = err_json.get('error')
            msg = err_json.get('message')
            print(f"{error}: {msg}")

        return resp.json()
    
    def refresh(self):
        url = f"{self.domain}/aaa/v1/refresh"

        print(f"refresh url: {url}")

        headers = {"Authorization": f"Bearer {self.refresh_token}"}
        resp = requests.get(url, headers=headers)

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

        