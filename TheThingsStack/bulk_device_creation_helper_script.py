"""
    Script to convert device details CSV into json format compatible with
    The Things Stack device import tool.

    USAGE:
        "python device_creation_csv_to_json_script.py devices.csv"
    OPTIONALLY:
        Include a target file destination for CSV with "-t " 

    See the README for more information.
    
    Jack Fletcher 2021
"""
from secrets import token_hex
import argparse
import json
import csv


IDS = ['device_id', 'dev_eui', 'join_eui']
ROOT_KEYS = ['app_key']


def parse_device_csv(filepath):
    """
    Read and interpret device CSV into a dict.
    - join_eui and/or app_key will be generated if not specified in the CVS.
    - Blank '(optional)' values are not included in the final JSON.
    - supports_join is set to True if not specified.
    """
    devices = []
    with open(filepath) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Instantiate nested dict elements
            device = {
                'ids': {},
                'root_keys': {}
            }
            # Propogate data from row into dict
            for key, value in row.items():
                # Handle ID values
                if key in IDS:
                    if (key == 'join_eui') & (value == ""):
                        value = generate_join_eui()
                    device['ids'][key] = value
                # Handle root key values
                elif key in ROOT_KEYS:
                    if value == "":
                        value = generate_app_key()
                    device['root_keys'][key] = {
                        'key': value
                    }
                # Handle optional values
                elif '(optional)' in key:
                    # Skip blank optional values
                    if value == '':
                        pass
                    # Remove the word optional from the key
                    else:
                        device[key.replace('(optional)', '')] = value
                else:
                    device[key] = value
            # OTAA assumed true unless otherwise specified
            if 'supports_join' not in device:
                device['supports_join'] = True
            devices.append(device)
    return devices


def write_json(data, filepath='devices.json'):
    """
    Dump data into a formatted json file
    """
    with open(filepath, 'w') as f:
        f.write(json.dumps(data, indent=4))


def generate_app_key(bytes=16):
    """
    Create a new valid app_key
    """
    key = token_hex(bytes)
    return key


def generate_join_eui(bytes=8):
    """
        Create a new random join_eui (EUI-64)
        Logic is based on on https://github.com/things-nyc/random-eui64
    """
    eui = bytearray.fromhex(token_hex(bytes))
    # Last two bits of byte 0 must be '10'
    eui[0] = (eui[0] & ~1) | 2
    eui = ''.join('{:02x}'.format(b) for b in eui)
    return eui


if __name__ == '__main__':
    parser_description = (
        'Convert device creation csv to TTS JSON import format'
    )
    parser = argparse.ArgumentParser(description=parser_description)
    parser.add_argument('file', help='source csv file')
    parser.add_argument(
        '-t', '--target', help='(optional) json file destination')
    args = parser.parse_args()
    devices = parse_device_csv(args.file)
    if args.target is None:
        write_json(devices)
    else:
        write_json(devices, args.target)

    print("JSON creation complete. Check file.")
