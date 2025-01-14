from eodms_dds import dds
import click
import boto3
import random
from db import EODMS_DB
import os

mappings = {
    "staging": {
        "bucket_name": "eodms-staging-image-products",
        "collections": {
            "RCMImageProducts": {
                "prefix": 'image/rcm/sar/l1/2022/noamer/mde30/',
                "year_idx": 4,
                "aeoid_idx": 8,
                "sensor_id": 88
            },
            "NAPL": {
                "prefix": "image/napl/napl/cuf/",
                "year_idx": 4,
                "aeoid_idx": 8,
                "sensor_id": 64
            },
            "SGBAirPhotos": {
                "prefix": "image/napl/napl/l1/2022/",
                "year_idx": 4,
                "aeoid_idx": 8,
                "sensor_id": 99
            },
            "Radarsat2": {
                "prefix": "image/radarsat_2/sar/l1/2023/noamer/",
                "year_idx": 4,
                "aeoid_idx": 8,
                "sensor_id": 28
            },
            "WorldView-2": {
                "prefix": "image/w2/w2/",
                "year_idx": 4,
                "aeoid_idx": 8,
                "sensor_id": 33
            },
            "Radarsat1": {
                "prefix": ""
            }
        }
    },
    "prod": {
        "bucket_name": ""
    }
}

def get_item(dds_api, collection, item_uuid, out_folder):

    # dds_api.refresh_aaa()

    # coll = "Radarsat2"
    # item_uuid = "ac7596d1-379c-4c32-a3c5-a058feadc9bc"

    print(f"collection: {collection}")
    print(f"item_uuid: {item_uuid}")

    item_info = dds_api.get_item(collection, item_uuid)

    print(f"Item info: {item_info}")

    # out_folder = "C:\\Working\\Development\\EODMS\\_packages\\py-eodms-api"

    if item_info is None:
        return None

    if 'download_url' not in item_info.keys():
        return None

    dds_api.download_item(os.path.abspath(out_folder))

    return item_info

def get_db_item(contents, collection, env):

    coll_map = mappings[env]['collections'][collection]

    db_res = []
    while len(db_res) == 0:
        print(f"\nGetting random object...")
        rand_idx = random.randint(0, len(contents)-1)
        random_img = contents[rand_idx]

        print(f"random_img: {random_img}")
        # answer = input("Press enter...")

        # Parse key
        key = random_img.get('Key')
        items = key.split('/')
        year = items[coll_map.get('year_idx')]
        sensor_id = coll_map.get('sensor_id')

        try:
            aeoid = items[coll_map.get('aeoid_idx')]
        except IndexError:
            continue

        print(f"year: {year}")
        print(f"aeoid: {aeoid}")

        db = EODMS_DB()

        sql_cmd = f'''
SELECT ai.unique_identifier,
	ci.sequence_id,
	ai.year,
	ai.sensor_id, 
	ai.order_key, 
	ci.start_datetime
FROM 
    eodms_wesdmc.archive_image ai 
INNER JOIN eodms_wesdmc.catalog_image ci
    ON ai.ci_sequence_id = ci.sequence_id
WHERE 
    ai.rejected = false 
    AND ai.sensor_id = {sensor_id} 
    --AND ci.public_good = true
    AND ai.year = {year}
    AND ai.aeoid = {aeoid}
ORDER BY ci.start_datetime DESC
LIMIT 100;
'''     
        # print(f"sql_cmd: {sql_cmd}")

        db_res = db.select(sql_cmd)
        print(f"db_res: {db_res}")

        if len(db_res) == 0:
            print("No image found in the database.")

    return db_res[0]

def run(eodms_user, eodms_pwd, collection, env, out_folder):

    # aaa_api = aaa.AAA_API(eodms_user, eodms_pwd, env)

    # aaa_api.get_token

    dds_api = dds.DDS_API(eodms_user, eodms_pwd, env)

    # regions = {'noamer'}
    # beam_modes = {'mde30'}
    bucket_name = mappings[env].get('bucket_name')
    s3_client = boto3.client('s3')

    coll_map = mappings[env]['collections'][collection]

    # object_prefix = f'image/rcm/sar/l1/2022/noamer/mde30/'
    object_prefix = coll_map.get('prefix')

    response = s3_client.list_objects_v2(Bucket=bucket_name,
                                         Prefix=object_prefix)
                                         #MaxKeys=100)
    
    contents = response.get('Contents')

    item_info = None
    while item_info is None:
        db_res = get_db_item(contents, collection, env)

        uuid = db_res.get('unique_identifier')

        item_info = get_item(dds_api, collection, uuid, out_folder)



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