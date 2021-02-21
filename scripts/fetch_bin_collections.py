#!/srv/homeassistant/bin/python3
#
# Scrape local COVID-19 case rate from data.gov.uk
# Returns a single floating point number in cases/100k.
#

from argparse import ArgumentParser, Namespace
import requests
from typing import Any, Dict, Optional

service_url = ('https://bcprdapidyna002.azure-api.net/'
               'bcprdfundyna001-alloy/NextCollectionDates')
api_key_header = {'Ocp-Apim-Subscription-Key':
                  '47ffd667d69c4a858f92fc38dc24b150'}


def get_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        description=("Fetch Bristol City Council recycling collection dates "
                     "for a given address, and display as simplified JSON."))
    parser.add_argument(
        'uprn',
        help=("Unique Property Reference Number for collection address (from "
              "https://maps.bristol.gov.uk/pinpoint/)."))
    return parser.parse_args()


def parse(r: Dict[str, Any]) -> str:
    bins = {
        '180L General Waste': 'Black',
        '240L Garden Waste Bin': 'Green'
        }

    def parse_container(container: Dict[str, Any]) -> Optional[str]:
        friendly_name = bins.get(container['containerName'])
        if friendly_name is not None:
            # Assume only one round per container, trim time off datetime
            # of collection.
            last_date = container['collection'][0]['lastCollectionDate'][:10]
            next_date = container['collection'][0]['nextCollectionDate'][:10]
            return (
                f'"{friendly_name}": {{'
                f'"last_date": "{last_date}", '
                f'"next_date": "{next_date}"}}')
        else:
            return None

    collections = map(parse_container, r["data"])
    if collections is not None:
        filtered = ", ".join(filter(lambda x: x is not None,
                                    list(collections)))  # type: ignore
        return (
            f'{{"status": "{r["status"]}", '
            f'"bins": {{{filtered}}}}}')
    else:
        return ('{{'
                '"status":"Failed", '
                '"status_code": "404", '
                '"error": "Couldn\'t find collections in server response"'
                '}}')


if __name__ == '__main__':
    args = get_args()

    response: requests.Response = requests.post(
        service_url,
        json={'uprn': args.uprn},
        headers=api_key_header)

    if response.ok:
        print(f"{parse(response.json())}")
    else:
        print((f'{{'
               f'"status":"Failed", '
               f'"status_code": "{response.status_code}", '
               f'"error": "{response.reason}"'
               f'}}'))
