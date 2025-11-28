from eodms_dds import dds, aaa
from pystac_client import Client
from typing import Optional, List, Dict, Any
# import json
import click
import os
import ssl
from requests.packages import urllib3

ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def search(aaa_api=None, environment='prod', 
                collections: Optional[List[str]] = None,
                bbox: Optional[List[float]] = None,
                datetime: Optional[str] = None,
                **kwargs) -> List[Dict[str, Any]]:
    """
    Search the EODMS STAC catalog using pystac_client.
    
    :param aaa_api: Optional AAA_API instance for authentication
    :param environment: Environment to use ('prod' or 'staging')
    :param collections: List of collection IDs to search
    :param bbox: Bounding box as [west, south, east, north]
    :param datetime: Temporal filter as ISO 8601 string or range
    :param kwargs: Additional search parameters
    :return: List of item dictionaries
    """
    
    domain = "https://www.eodms-sgdot.nrcan-rncan.gc.ca"
    search_endpoint = f"{domain}/search"
    
    # Prepare headers with authentication if available
    headers = {}
    if aaa_api:
        access_token = aaa_api.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        print("Using authenticated search")
    else:
        print("Using unauthenticated search")
    
    # Open STAC catalog with optional authentication
    if headers:
        client = Client.open(search_endpoint, headers=headers)
    else:
        client = Client.open(search_endpoint)
    
    # Build search parameters
    search_params = {}
    
    if collections:
        search_params['collections'] = collections
    
    if bbox:
        search_params['bbox'] = bbox
    
    if datetime:
        search_params['datetime'] = datetime
    
    # Add any additional parameters
    search_params.update(kwargs)
    
    # Execute search
    search = client.search(**search_params, method='GET')
    search_results = search.item_collection()
    
    # Convert to list of dictionaries
    items = [item.to_dict() for item in search_results]
    
    print(f"Found {len(items)} items")
    
    return items

def download(dds_api, collection, item_uuid, out_folder):

    item_info = dds_api.get_item(collection, item_uuid)

    if item_info is None:
        return None

    if 'download_url' not in item_info.keys():
        return None

    dds_api.download_item(os.path.abspath(out_folder))

    return item_info

def run(eodms_user, eodms_pwd, collection, env, out_folder, datetime_range=None, bbox=None, uuid=None):

    # Create shared AAA instance
    aaa_api = aaa.AAA_API(eodms_user, eodms_pwd) if eodms_user and eodms_pwd else None

    dds_api = dds.DDS_API(aaa_api, env)

    # If UUID is provided, skip search and download directly
    if uuid:
        print(f"Downloading image with UUID: {uuid}")
        download(dds_api, collection, uuid, out_folder)
        return

    # Search using pystac_client with shared AAA instance
    items = search(
        aaa_api=aaa_api,
        environment=env,
        collections=[collection],
        datetime=datetime_range,
        bbox=bbox
    )
    
    if items and len(items) > 0:
        uuid = items[0].get('id')
        print(f"Downloading the first image (UUID: {uuid}) from the list")
        download(dds_api, collection, uuid, out_folder)


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--username', '-u', required=False, help='The EODMS username.')
@click.option('--password', '-p', required=False, help='The EODMS password.')
@click.option('--collection', '-c', required=True, help='The collection name.')
@click.option('--uuid', required=False, default=None, help='The UUID of the image to download (skips search).')
@click.option('--datetime', '-d', required=False, default=None,
              help='Temporal filter as ISO 8601 string or range (e.g., "2023-01-01/2023-12-31").')
@click.option('--bbox', '-b', required=False, default=None,
              help='Bounding box as comma-separated values: west,south,east,north (e.g., "-100,45,-95,50").')
@click.option('--env', '-e', required=False, default='prod', 
              help='The AWS environment.')
@click.option('--out_folder', '-o', required=False, default='.',
              help='The output folder.')
def cli(username, password, collection, uuid, datetime, bbox, env, out_folder):
    """
    Search and Download images from EODMS STAC catalog and DDS.
    
    Examples:
    
    \b
    # Search and download first RCM image
    python stac_dds_test.py -u USER -p PASS -c RCMImageProducts
    
    \b
    # Search with datetime filter
    python stac_dds_test.py -u USER -p PASS -c RCMImageProducts -d "2023-01-01/2023-12-31"
    
    \b
    # Search with bounding box (west,south,east,north)
    python stac_dds_test.py -u USER -p PASS -c RCMImageProducts -b "-100,45,-95,50"
    
    \b
    # Download specific image by UUID (skips search)
    python stac_dds_test.py -u USER -p PASS -c RCMImageProducts --uuid 12345678-1234-1234-1234-123456789abc
    
    \b
    # Specify output folder
    python stac_dds_test.py -u USER -p PASS -c RCMImageProducts -o ./downloads
    """
    
    # Parse bbox string to list of floats
    bbox_list = None
    if bbox:
        try:
            bbox_list = [float(x.strip()) for x in bbox.split(',')]
            if len(bbox_list) != 4:
                raise ValueError("Bounding box must have exactly 4 values")
        except ValueError as e:
            click.echo(f"Error parsing bbox: {e}", err=True)
            return

    run(username, password, collection, env, out_folder, datetime, bbox_list, uuid)

if __name__ == '__main__':
    cli()