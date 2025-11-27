from eodms_dds import dds
from eodms_dds import search
# import json
import click
import os

def get_item(dds_api, collection, item_uuid, out_folder):

    item_info = dds_api.get_item(collection, item_uuid)

    if item_info is None:
        return None

    if 'download_url' not in item_info.keys():
        return None

    dds_api.download_item(os.path.abspath(out_folder))

    return item_info

def run(eodms_user, eodms_pwd, collection, env, out_folder):

    dds_api = dds.DDS_API(eodms_user, eodms_pwd, env)

    search_api = search.Search_API(eodms_user, eodms_pwd, env)

    res = search_api.search_items(collections=[collection], datetime="2024-01-01/2025-12-31")
    #print(f"Number of results: {len(res)}")
    #if res and len(res) > 0:
        #uuid = res[0].get('id')
        #get_item(dds_api, collection, uuid, out_folder)


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--username', '-u', required=True, help='The EODMS username.')
@click.option('--password', '-p', required=True, help='The EODMS password.')
@click.option('--collection', '-c', required=True, help='The collection name.')
@click.option('--env', '-e', required=False, default='prod', 
              help='The AWS environment.')
@click.option('--out_folder', '-o', required=False, default='.',
              help='The output folder.')
# @click.option('--uuid', '-u', required=True, help='The UUID of the image.')
def cli(username, password, collection, env, out_folder):
    """
    Used for CLI input.
    """

    run(username, password, collection, env, out_folder)

if __name__ == '__main__':
    cli()