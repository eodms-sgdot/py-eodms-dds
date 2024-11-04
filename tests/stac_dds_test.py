from eodms_dds import dds
from eodms_stac import stac
# import json
import click
import os

def get_item(dds_api, collection, item_uuid, out_folder):

    dds_api.refresh_aaa()

    item_info = dds_api.get_item(collection, item_uuid)

    if item_info is None:
        return None

    if 'download_url' not in item_info.keys():
        return None

    dds_api.download_item(os.path.abspath(out_folder))

    return item_info

def run(eodms_user, eodms_pwd, collection, env, out_folder):

    dds_api = dds.DDS_API(eodms_user, eodms_pwd, env)

    stac_api = stac.EODMSSTAC() #eodms_user, eodms_pwd)

    if collection == "RCMImageProducts":
        stac_coll = "rcm"

    res = stac_api.search(paged=True, collections=stac_coll, limit=20)

    uuid = res.get('features')[5].get('id')

    get_item(dds_api, collection, uuid, out_folder)


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