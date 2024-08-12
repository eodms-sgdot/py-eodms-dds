EODMS API Client
================

## Clone Repository

```bash
git clone https://github.com/eodms-sgdot/py-eodms-api.git
```

## Package Installation

```bash
cd py-eodms-api
pip install -e .
```

## Testing

### Set Environment Variables

Before running the `./tests/_set_vars.ps1` in Powershell, replace the environment variable entries.

Now run the Powershell script:

```powershell
_set_vars.ps1
```

### Run the Test

Usage:

```
Usage: rnd_pkg_test.py [OPTIONS]

  Used for CLI input.

Options:
  -u, --username TEXT    The EODMS username.  [required]
  -p, --password TEXT    The EODMS password.  [required]
  -c, --collection TEXT  The collection name.  [required]
  -e, --env TEXT         The AWS environment.  [required]
  -o, --out_folder TEXT  The output folder.
  -h, --help             Show this message and exit.
```

```bash
python rnd_pkg_test.py -u eodms_user -p eodms_pwd -c NAPL -e staging
```