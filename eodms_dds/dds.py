import os
import requests
from requests.packages import urllib3
from urllib.parse import urlparse
from tqdm.auto import tqdm
import ssl

from . import aaa

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DDS_API():

    def __init__(self, username, password, environment='prod'):
        self.domain = "https://www.eodms-sgdot.nrcan-rncan.gc.ca"

        self.img_info = None

        if environment == 'staging':
            self.domain = os.environ.get('DOMAIN')

        # print(f"ssl.get_server_certificate(): {ssl.get_server_certificate(self.domain)}")

        self.header = '| EODMS_DDS | '

        self.aaa = aaa.AAA_API(username, password, environment)

        # self.login_info = self.aaa.login()

    def get_item(self, collection, item_uuid, catalog="EODMS"):

        url = f"{self.domain}/dds/v1/item/{catalog}/{collection}/{item_uuid}"

        access_token = self.aaa.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        # resp = requests.get(url, headers=headers, trust_env=False, verify=False)
        resp = self.aaa.prepare_request(url, headers=headers)

        if resp.status_code == 200:
            print(f"\n{self.header}Successfully got item using DDS API")
            try:
                self.img_info = resp.json()
            except:
                if resp.content.startswith('<HTML>'):
                    print(f"{self.header}DDS API cannot be accessed at this "
                          f"time.")
                    return None
        elif resp.status_code == 202:
            self.img_info = resp.json()
            status = self.img_info.get('status')
            print(f"{self.header}Image is being processed. Its current " 
                  f"status is {status}.")
        else:
            print(f"\n{self.header}Failed to get item using DDS API\n")
            try:
                err_json = resp.json()
                error = err_json.get('error')
                msg = err_json.get('message')
                print(f"{error}: {msg}")
            except:
                # print(f"resp: {resp.content}")
                return None

        return resp.json()

    def download_item(self, out_folder):

        if self.img_info is None:
            print(f"\n{self.header}ERROR: No image info available.\n")
            return None

        download_url = self.img_info.get('download_url')

        if not download_url:
            return None

        url_parsed = urlparse(download_url)
        dest_fn = os.path.join(out_folder, os.path.basename(url_parsed.path))

        print(f"\n{self.header}Downloading image to {dest_fn}...\n")
        # print(f"download url: {download_url}")

        # resp = requests.head(download_url, allow_redirects=True, verify=False)
        # resp_header = resp.headers
        # fsize = resp_header.get('Content-Length')
        # open(fname, 'wb').write(resp.content)

        with requests.get(download_url, stream=True, verify=False) as stream:
            with open(dest_fn, 'wb') as pipe:
                with tqdm.wrapattr(
                        pipe,
                        method='write',
                        miniters=1,
                        desc=os.path.basename(dest_fn)
                ) as file_out:
                    for chunk in stream.iter_content(chunk_size=1024):
                        file_out.write(chunk)

        # response = requests.get(download_url, stream=True) #, verify=False)
        # if dest_fn is None:
        #     return response.content
        # open(dest_fn, "wb").write(response.content)
