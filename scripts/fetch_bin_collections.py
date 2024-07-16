#!/usr/local/bin/python3
#
# Scrape local COVID-19 case rate from data.gov.uk
# Returns a single floating point number in cases/100k.
#

from argparse import ArgumentParser, Namespace
from datetime import datetime
import json
import requests
from typing import Any, Dict

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


def parse(r: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    bins = [
        {
            'name': 'Black',
            'description': '180L General Waste'
        },
        {
            'name': 'Green',
            'description': '240L Garden Waste Bin'
        },
        {
            'name': 'Box',
            'description': '55L Green Recycling Box'
        },
        {
            'name': 'Tree',
            'description': 'Christmas Tree'
        }
    ]

    def check_date(date: str) -> str:
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return date
        except ValueError:
            return "Unknown"

    def find_collection(description: str) -> Dict[str, str]:
        container = list(filter(lambda x: x['containerName'] == description,
                         r['data']))

        if container != []:
            collection = list(container)[0]['collection'][0]
            return {
               'last': check_date(collection['lastCollectionDate'][:10]),
               'next': check_date(collection['nextCollectionDate'][:10])
            }
        else:
            return {
               'last': 'Unknown',
               'next': 'Unknown'
            }

    return {bin['name']: find_collection(bin['description']) for bin in bins}


if __name__ == '__main__':
    args = get_args()

    response: requests.Response = requests.post(
        service_url,
        json={'uprn': args.uprn},
        headers=api_key_header)

    if response.ok:
        print(json.dumps({
                            'status': 'OK',
                            'bins': parse(response.json())
                        }))
    else:
        print(json.dumps({
                            'status': 'Failed',
                            'status_code': response.status_code,
                            'error': response.reason
                         }))
