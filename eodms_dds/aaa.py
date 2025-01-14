import requests
from requests.packages import urllib3
import ssl
import os
import json
# import time
from datetime import datetime, timedelta
import dateparser

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AAA_Creds():

    def __init__(self):

        self.access_token = None
        self.refresh_token = None
        self.access_exp = None
        self.refresh_exp = None

        self.cred_fn = None

    def get_json(self):
        """
        Gets a JSON of the credentials
        """

        access_str = self.access_exp
        if isinstance(access_str, datetime):
            access_str = access_str.isoformat()

        refresh_str = self.refresh_exp
        if isinstance(refresh_str, datetime):
            refresh_str = refresh_str.isoformat()

        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "access_expiration": access_str,
            "refresh_expiration": refresh_str
        }
    
    def set_vals(self, **kwargs):
        """
        Sets one or multiple variables.

        :param kwargs:
            - access_token
            - refresh_token
            - access_exp
            - refresh_exp
        """

        if 'access_token' in kwargs:
            print("\nUpdating Access Token...")
            self.access_token = kwargs.get('access_token')

        if 'refresh_token' in kwargs:
            print("\nUpdating Refresh Token...")
            self.refresh_token = kwargs.get('refresh_token')

        if 'access_exp' in kwargs:
            dt = kwargs.get('access_exp')
            print(f"\nUpdating Access Expiration with {dt}...")
            self.access_exp = dt

        if 'refresh_exp':
            dt = kwargs.get('refresh_exp')
            print(f"\nUpdating Refresh Expiration with {dt}...")
            self.refresh_exp = dt

    def set_fn(self, fn):
        """
        Sets the aaa_creds.json path.
        """

        self.cred_fn = fn

    def get_access_exp(self, as_dt=True):
        """
        Returns the Access Token expiration time.

        :param as_dt: Determines whether to return the time as a datetime.
        :type  as_dt: boolean
        """

        if as_dt:
            return dateparser.parse(self.access_exp)
        
        return self.access_exp
    
    def get_refresh_exp(self, as_dt=True):
        """
        Returns the Refresh Token expiration time.

        :param as_dt: Determines whether to return the time as a datetime.
        :type  as_dt: boolean
        """

        if as_dt:
            return dateparser.parse(self.refresh_exp)
        
        return self.refresh_exp

    def export_vals(self):
        """
        Exports the credential values to the aaa_creds.json file.
        """

        print(f"self.get_json: {self.get_json()}")
        answer = input("Press enter...")

        with open(self.cred_fn, 'w') as f:
            json.dump(self.get_json(), f)

    def import_vals(self):
        """
        Imports the credential values from the aaa_creds.json file.
        """

        if not os.path.exists(self.cred_fn):
            return None

        with open(self.cred_fn, 'r') as file:
            creds = json.load(file)

        self.access_token = creds.get('access_token')
        self.refresh_token = creds.get('refresh_token')

        self.access_exp = datetime.fromisoformat(creds.get('access_expiration'))
        self.refresh_exp = datetime.fromisoformat(creds.get('refresh_expiration'))

        # print("Values from aaa_creds.json:")
        # print(f"  Access Token: {self.access_token}")
        # print(f"  Refresh Token: {self.refresh_token}")
        print(f"\nAccess Expiration: {self.access_exp}")
        print(f"Refresh Expiration: {self.refresh_exp}")

class AAA_API():

    def __init__(self, username, password, environment='prod'):

        self.aaa_creds = AAA_Creds()

        self.username = username
        self.password = password

        self.domain = "https://www.eodms-sgdot.nrcan-rncan.gc.ca"

        if environment == 'staging':
            self.domain = os.environ.get('DOMAIN')

        print(f"self.domain: {self.domain}")

        # self.access_token = None
        # self.refresh_token = None

        user_folder = os.path.expanduser('~')
        self.auth_folder = os.path.join(user_folder, '.eodms')
        self.aaa_creds.set_fn(os.path.join(self.auth_folder, 'aaa_creds.json'))

        if not os.path.exists(self.auth_folder):
            os.makedirs(self.auth_folder)

        self.login_success = True

    # def _save_tokens(self, fn):
    #     # Store the tokens
    #     with open(fn, 'w') as f:
    #         json.dump(self.cred_dict, f)

    # def _load_tokens(self, fn):
    #     with open(fn, 'r') as file:
    #         self.cred_dict = json.load(file)
    
    # def _print_times(self):

    #     ses_time_str = str(timedelta(seconds=self.session_time))
    #     ref_time_str = str(timedelta(seconds=self.refresh_time))
            
    #     print(f"\nTotal session time: {ses_time_str}")
    #     print(f"Total refresh time: {ref_time_str}\n")

    def get_access_token(self):
        """
        Gets a new Access Token using either an existing Access Token, 
            the "refresh" endpoint or "login"
            depending on the expiration dates of the current tokens.

        Ex:
            - existing Access Token if both tokens have not expired
            - "refresh" if the Access Token has expired but the Refresh
                Token has not
            - "loging" if both tokens have expired
        """

        self.aaa_creds.import_vals()

        if self.aaa_creds.access_token is None:
            self._login()
            return self.aaa_creds.access_token

        now_dt = datetime.now()
        access_exp = self.aaa_creds.access_exp
        refresh_exp = self.aaa_creds.refresh_exp

        if now_dt >= access_exp and now_dt >= refresh_exp:
            print(f"\nCurrent Refresh Token has expired. Getting new Tokens...")

            # Get a new token
            self._login()
        elif now_dt >= access_exp and now_dt < refresh_exp:
            print("\nCurrent Access Token has expired. " \
                  "Getting a new Access Token using current Refresh Token...")

            self._refresh()

        if not self.login_success:
            print(f"\nWARNING: Could not access current AAA session with " \
                  f"existing tokens in {self.aaa_creds.cred_fn}")

        return self.aaa_creds.access_token

    def calculate_expirations(self):
        """
        Calculates the expiration times for the Access Token 
            and the Refresh Token.
        """

        # Determine the expiration times
        refresh_time = self.response.get('refresh_token_expires_in')
        access_time = self.response.get('expires_in')
        now_dt = datetime.now()
        self.access_exp = now_dt + timedelta(seconds=access_time)
        self.refresh_exp = now_dt + timedelta(seconds=refresh_time)

        self.aaa_creds.set_vals(access_exp=self.access_exp,
                                refresh_exp=self.refresh_exp)

    def _login(self):
        """
        Starts a new session using the "login" endpoint of the AAA API 
            and gets the Access Token.
        """

        url = f"{self.domain}/aaa/v1/login"

        payload = {
            "grant_type": "password",
            "password": self.password,
            "username": self.username
        }

        resp = requests.post(url, json=payload, verify=False) #, verify=False)

        # print(f"\nlogin resp: {resp.content}")

        if resp.status_code == 200:
            print("\nSuccessfully logged in using AAA API")

            self.response = resp.json()

            self.calculate_expirations()

            new_access_token = self.response.get('access_token')
            new_refresh_token = self.response.get('refresh_token')
            self.aaa_creds.set_vals(access_token=new_access_token,
                                    refresh_token=new_refresh_token,
                                    access_exp=self.access_exp.isoformat(),
                                    refresh_exp=self.refresh_exp.isoformat())
            
            self.aaa_creds.export_vals()

            # self._print_times()

            self.login_success = True

        else:
            err_json = resp.json()
            error = err_json.get('error')
            msg = err_json.get('message')
            print(f"\nWARNING: Failed to log in using AAA API: {error}: {msg}")
            self.login_success = False

            if resp.status_code == 429:
                print("\nAttempting to get new Access Token using existing " \
                      "Refresh Token...")
                self._refresh()

    def _refresh(self):
        """
        Gets a new Access Token using an existing Refresh Token 
            and the "refresh" endpoint of the AAA API.
        """

        url = f"{self.domain}/aaa/v1/refresh"

        # print(f"refresh url: {url}")

        # resp = requests.get(url, verify=False)

        headers = {"Authorization": f"Bearer {self.aaa_creds.refresh_token}"}
        # print(f"headers: {headers}")
        resp = requests.get(url, headers=headers, verify=False)

        # print(f"\nrefresh resp: {resp.content}")

        if resp.status_code == 200:
            print("\nSuccessfully refreshed using AAA API")
            self.response = resp.json()

            self.calculate_expirations()

            new_access_token = self.response.get('access_token')

            self.aaa_creds.set_vals(access_token=new_access_token)
            self.aaa_creds.export_vals()

            self.login_success = True
        else:
            err_json = resp.json()
            error = err_json.get('error')
            msg = err_json.get('message')
            print(f"\nWARNING: Failed to refresh using AAA API: {error}: {msg}")
            self.login_success = False


        