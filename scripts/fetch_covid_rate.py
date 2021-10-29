#!/srv/homeassistant/bin/python3
#
# Scrape local COVID-19 case rate from data.gov.uk
# Returns a single floating point number in cases/100k.
#

from argparse import ArgumentParser, Namespace
from urllib.parse import quote_plus
from urllib.request import urlopen
from bs4 import BeautifulSoup      # type: ignore
import json

url: str = "https://coronavirus.data.gov.uk/search?postcode="


def get_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser(description=(
      "Fetch local COVID rate information for given UK postcode."))
    parser.add_argument('postcode')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    html = urlopen(url + quote_plus(args.postcode))
    result = {
        'rate': 'Unknown',
        'date': 'Unknown'
    }
    soup: BeautifulSoup = BeautifulSoup(html, 'lxml')
    x = soup.find_all('span', {'class', 'number-link'})
    if len(x) > 1:
        result.update({'rate': x[1].text})
    for x in soup.find_all('time'):
        if x.parent['id'] == "last-update" and x.has_attr('datetime'):
            result.update({'date': x['datetime']})
            break
    print(json.dumps(result))
