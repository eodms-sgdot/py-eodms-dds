import os
import requests
from requests.packages import urllib3
import ssl
from pystac_client import Client
from typing import Optional, List, Dict, Any

from . import aaa
from . import api_logger

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Search_API():

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, environment: str = 'prod'):
        """
        Initialize the Search API.
        
        :param username: Optional username for AAA authentication
        :param password: Optional password for AAA authentication
        :param environment: Environment to use ('prod' or 'staging')
        """

        # ssl_cert_path = os.path.expanduser('C:/Users/wmackinn/.aws/nrcan+azure+amazon.cer')
        # os.environ['SSL_CERT_FILE'] = ssl_cert_path
        # os.environ['REQUESTS_CA_BUNDLE'] = ssl_cert_path
        # os.environ['CURL_CA_BUNDLE'] = ssl_cert_path
        # os.environ['AWS_CA_BUNDLE'] = ssl_cert_path
        # os.path.exists(ssl_cert_path)

        self.domain = "https://www.eodms-sgdot.nrcan-rncan.gc.ca"
        #self.domain = "https://www-staging-eodms.aws.nrcan-rncan.cloud"
        self.search_endpoint = f"{self.domain}/search"

        if environment == 'staging':
            self.domain = os.environ.get('DOMAIN')
            self.search_endpoint = f"{self.domain}/search"

        self.logger = api_logger.EODMSLogger('EODMS_Search', api_logger.eodms_logger)

        # Initialize AAA if credentials provided
        self.aaa = None
        if username and password:
            self.aaa = aaa.AAA_API(username, password)
            self.logger.info("AAA authentication initialized")

    def search(self, 
               collections: Optional[List[str]] = None,
               bbox: Optional[List[float]] = None, 
               datetime: Optional[str] = None,
               **kwargs) -> Any:
        """
        Search the EODMS STAC catalog using pystac_client.
        
        :param collections: List of collection IDs to search
        :param bbox: Bounding box as [west, south, east, north]
        :param datetime: Temporal filter as ISO 8601 string or range (e.g., "2023-01-01/2023-12-31")
        :param kwargs: Additional search parameters passed to pystac_client
        :return: ItemCollection from pystac_client search
        """
        
        # Prepare headers with authentication if available
        headers = {}
        if self.aaa:
            access_token = self.aaa.get_access_token()
            headers = {"Authorization": f"Bearer {access_token}"}
            self.logger.info("Using authenticated search")
        else:
            self.logger.info("Using unauthenticated search")

        try:
            # Open STAC catalog with optional authentication
            if headers:
                client = Client.open(
                    self.search_endpoint,
                    headers=headers
                )
            else:
                client = Client.open(self.search_endpoint)
            
            auth_status = "with authentication" if headers else "without authentication"
            self.logger.info(f"Connected to STAC catalog at {self.search_endpoint} {auth_status}")

            # List available collections
            collections_list = list(client.get_collections())
            self.logger.info(f"Available collections: {[c.id for c in collections_list]}")
            # Build search parameters
            search_params = {}
            
            if collections:
                search_params['collections'] = collections
                self.logger.info(f"Searching collections: {collections}")
            
            if bbox:
                search_params['bbox'] = bbox
                self.logger.info(f"Searching with bbox: {bbox}")
            
            if datetime:
                search_params['datetime'] = datetime
                self.logger.info(f"Searching with datetime: {datetime}")

            # Add any additional parameters
            search_params.update(kwargs)

            # Execute search
            search = client.search(
                collections=['RCMImageProducts']
            )
  
            search_results = search.item_collection()
            
            self.logger.info("Search completed successfully")
            
            return search_results

        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            raise

    def search_items(self,
                     collections: Optional[List[str]] = None,
                     bbox: Optional[List[float]] = None,
                     datetime: Optional[str] = None,
                     **kwargs) -> List[Dict[str, Any]]:
        """
        Search and return items as a list of dictionaries.
        
        :param collections: List of collection IDs to search
        :param bbox: Bounding box as [west, south, east, north]
        :param datetime: Temporal filter as ISO 8601 string or range
        :param kwargs: Additional search parameters
        :return: List of item dictionaries
        """
        
        search_results = self.search(
            collections=collections,
            bbox=bbox,
            datetime=datetime,
            **kwargs
        )
        
        # Convert to list of dictionaries
        items = [item.to_dict() for item in search_results]
        
        self.logger.info(f"Found {len(items)} items")
        
        return items
