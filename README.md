EODMS DDS API Client
====================

## Pip Installation

```bash
pip install git+https://github.com/eodms-sgdot/py-eodms-dds.git
```

## Usage

### Get and Download Image

> **_NOTE:_** Before using the DDS API, you'll need to get the UUID of an RCM image product. You can use the [py-eodms-rapi](https://github.com/eodms-sgdot/py-eodms-rapi) (see [rapi_dds_test.py](./tests/rapi_dds_test.py) for example code).

```python
# First, create the DDS_API with your EODMS username and password.
dds_api = dds.DDS_API(eodms_user, eodms_pwd)

# Set the Collection Id and the UUID
collection = 'RCMImageProducts'
item_uuid = '01d0c4e2-853b-5d05-b48f-7d768bb249c5'

# Once the DDS_API has been initialized, you can now get an item with a UUID and the Collection Id.
item_info = dds_api.get_item(collection, item_uuid)

# NOTE: item_info is also stored as self.item_info in the DDS_API object.

# Download the image to a specific location (the download link will be taken from the self.item_info)
out_folder = "/home/myuser"
dds_api.download_item(out_folder)
```

### Refresh Session

Each run of a script will require a refresh of the DDS API session. Previous tokens are stored in JSON files in `.eodms/aaa_auth` under the user folder.

```python
dds_api.refresh_aaa()
```

## Testing

### Clone Repository

```bash
git clone https://github.com/eodms-sgdot/py-eodms-dds.git
```

### Package Installation

If the pip installation above did not work, you can install from the cloned repository:

```bash
cd py-eodms-dds
pip install -e .
```

### Run rapi_dds_test.py

This test gets an image item from the EODMS RAPI, parses the metadata and uses the UUID to download the image using the EODMS DDS API.

For this test script, you will need to install the [py-eodms-rapi](https://github.com/eodms-sgdot/py-eodms-rapi) package:

```bash
pip install py-eodms-rapi -U
```

```
Usage: rapi_dds_test.py [OPTIONS]

  Used for CLI input.

Options:
  -u, --username TEXT    The EODMS username.  [required]
  -p, --password TEXT    The EODMS password.  [required]
  -c, --collection TEXT  The collection name.  [required]
  -e, --env TEXT         The AWS environment (default is "prod").
  -o, --out_folder TEXT  The output folder (default is the current folder).
  -h, --help             Show this message and exit.
```

```bash
python rapi_dds_test.py -u eodms_user -p eodms_pwd -c RCMImageProducts
```

### Run stac_dds_test.py

This test gets an image item from the EODMS STAC API and uses the `id` (UUID) to download the image using the EODMS DDS API.

This script requires the [py-eodms-stac](https://github.com/eodms-sgdot/py-eodms-stac):

```bash
cd tests
git clone https://github.com/eodms-sgdot/py-eodms-stac.git

cd py-eodms-stac
pip install -e .
```

```
Usage: stac_dds_test.py [OPTIONS]

  Used for CLI input.

Options:
  -u, --username TEXT    The EODMS username.  [required]
  -p, --password TEXT    The EODMS password.  [required]
  -c, --collection TEXT  The collection name.  [required]
  -e, --env TEXT         The AWS environment (default is "prod").
  -o, --out_folder TEXT  The output folder (default is the current folder).
  -h, --help             Show this message and exit.
```

```bash
python stac_dds_test.py -u eodms_user -p eodms_pwd -c RCMImageProducts  
```
