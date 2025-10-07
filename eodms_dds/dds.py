import os
import requests
from requests.packages import urllib3
from urllib.parse import urlparse
from tqdm.auto import tqdm
import ssl

from . import aaa
from . import api_logger

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# class DDSUnavailableException(Exception):
#     pass

# class DDSAuthException(Exception):
#     pass

# class DDSException(Exception):
#     pass

class DDS_API():

    def __init__(self, username, password, environment='prod'):
        self.domain = "https://www.eodms-sgdot.nrcan-rncan.gc.ca"

        self.img_info = None

        if environment == 'staging':
            self.domain = os.environ.get('DOMAIN')

        self.logger = api_logger.EODMSLogger('EODMS_DSS', api_logger.eodms_logger)

        # self.logger.debug((f"ssl.get_server_certificate(): {ssl.get_server_certificate(self.domain)}")

        self.aaa = aaa.AAA_API(username, password)

        # self.login_info = self.aaa.login()

    def get_item(self, collection, item_uuid, catalog="EODMS"):

        url = f"{self.domain}/dds/v1/item/{catalog}/{collection}/{item_uuid}"

        access_token = self.aaa.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        # resp = requests.get(url, headers=headers, trust_env=False, verify=False)
        resp = self.aaa.prepare_request(url, headers=headers)

        if resp.status_code == 200:
            self.logger.info("Successfully got item using DDS API")
            try:
                self.img_info = resp.json()
            except requests.exceptions.JSONDecodeError as exception:
                content_type = resp.headers["Content-Type"]
                if "text/html" in content_type:
                    self.logger.info("DDS API cannot be accessed at this time.")
                    return None
                else:
                    raise exception
        elif resp.status_code == 202:
            self.img_info = resp.json()
            status = self.img_info.get('status')
            self.logger.info(f"Image is being processed. Its current "
                  f"status is {status}.")
        else:
            try:
                err_json = resp.json()
                error = err_json.get('error')
                msg = err_json.get('message')
                self.logger.error(
                    "Failed to get item using DDS API\n\n"
                    f"{error}: {msg}"
                )
            except:
                self.logger.error("Failed to get item using DDS API\n")
                #  self.logger.error(f"resp: {resp.content}")
                return None

        return resp.json()

    def download_item(self, out_folder) -> str:
        """
        Downloads the item to the specified folder.
        Returns the filename (full path).
        """

        if self.img_info is None:
            self.logger.error("ERROR: No image info available.\n")
            return None

        download_url = self.img_info.get('download_url')

        if not download_url:
            return None

        url_parsed = urlparse(download_url)
        dest_fn = os.path.join(out_folder, os.path.basename(url_parsed.path))

        self.logger.info(f"Downloading image to {dest_fn}...\n")

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

        return dest_fn
