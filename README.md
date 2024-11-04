EODMS API Client
================

## Clone Repository

```bash
git clone https://github.com/eodms-sgdot/py-eodms-dds.git
```

## Package Installation

```bash
cd py-eodms-dds
pip install -e .
```

## Testing

### Run rapi_dds_test.py

This test gets an image item from the EODMS RAPI, parses the metadata and uses the UUID to download the image using the EODMS DDS API.

For this test script, you will need to install the `py-eodms-rapi` package:

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

This script requires the `py-eodms-stac`:

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