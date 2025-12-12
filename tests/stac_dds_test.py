from eodms_dds import dds, aaa, config
from pystac_client import Client
from typing import Optional, List, Dict, Any
# import json
import click
import os
import ssl
import requests
from requests.packages import urllib3
from urllib.parse import unquote
from urllib.parse import urlparse, parse_qs

def search(aaa_api=None, environment='prod', 
                collections: Optional[List[str]] = None,
                bbox: Optional[List[float]] = None,
                datetime: Optional[str] = None,
                limit = 100,
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
    
    domain_config = config.get_domain_config(environment)
    domain = domain_config['domain']
    search_endpoint = f"{domain}/search"
    verify_ssl = domain_config.get('verify_ssl', True)
    
    # Create a custom session with verify setting
    session = requests.Session()
    session.verify = verify_ssl
    
    # Prepare headers with authentication if available
    headers = {}
    if aaa_api:
        access_token = aaa_api.get_access_token()
        if not access_token:
            print("Authentication failed - no access token available")
            return []
        headers = {"Authorization": f"Bearer {access_token}"}
        print(f"Using authenticated search: {search_endpoint}")
    else:
        print(f"Using unauthenticated search: {search_endpoint}")
    
    # Open client with custom session
    if environment == 'staging':
        client = Client.open(
            search_endpoint, 
            headers=headers if headers else None,
            request_modifier=lambda request: setattr(session, 'verify', verify_ssl) or request
        )
        client._stac_io.session = session
    else:
        client = Client.open(search_endpoint, headers=headers if headers else None)
    
    # Print available collections
    print("Available collections:")
    for collection in client.get_collections():
        print(f"  - {collection.id}")
    print()

    # Build search parameters
    search_params = {}

    search_params['limit'] = limit
    
    if collections:
        search_params['collections'] = collections
    
    if bbox:
        search_params['bbox'] = bbox
    
    if datetime:
        search_params['datetime'] = datetime
    
    # Add any additional parameters
    search_params.update(kwargs)
    
    # Execute search
    try:
        items = []
        
        print(f"Searching for up to {limit} items...")
        search = client.search(**search_params, method='GET')
        print(unquote(search.url_with_parameters()))
        
        search_results = search.item_collection()
        
        # Convert to list of dictionaries
        items = [item.to_dict() for item in search_results]
        print(f"Retrieved {len(items)} items")
        
        # Trim to limit if we retrieved more
        items = items[:limit]
        print(f"Found {len(items)} items (limited to {limit})")

    except Exception as e:
        print(f"Search error: {e}")
        return []
    
    return items

def download(dds_api, collection, item_uuid, out_folder):

    item_info = dds_api.get_item(collection, item_uuid)

    if item_info is None:
        return None

    if 'download_url' not in item_info.keys():
        return None

    dds_api.download_item(os.path.abspath(out_folder))

    return item_info

def run(eodms_user, eodms_pwd, collection, env, out_folder, datetime_range=None, bbox=None, uuid=None, limit=100):

    # Create shared AAA instance
    aaa_api = aaa.AAA_API(eodms_user, eodms_pwd, env) if eodms_user and eodms_pwd else None

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
        bbox=bbox,
        limit=limit
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
@click.option('--limit', '-l', required=False, default=1000, type=int,
              help='Maximum number of items to fetch from search (default: 1000).')
@click.option('--env', '-e', required=False, default='prod', help='Defaults to "prod". If "staging", define `EODMS_STAGING_DOMAIN` env variable.')
@click.option('--out_folder', '-o', required=False, default='.',
              help='The output folder.')
def cli(username, password, collection, uuid, datetime, bbox, limit, env, out_folder):
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
    # Search with limit
    python stac_dds_test.py -u USER -p PASS -c RCMImageProducts -l 50
    
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

    run(username, password, collection, env, out_folder, datetime, bbox_list, uuid, limit)

if __name__ == '__main__':
    cli()