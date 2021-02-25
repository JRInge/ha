#!/srv/homeassistant/bin/python3
#
# Scrape local COVID-19 case rate from data.gov.uk
# Returns a single floating point number in cases/100k.
#

from argparse import ArgumentParser, Namespace
from urllib.parse import quote_plus
from urllib.request import urlopen
from bs4 import BeautifulSoup      # type: ignore
from bs4.element import ResultSet, Tag  # type: ignore

url: str = "https://coronavirus.data.gov.uk/search?postcode="


def get_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser(description=(
      "Fetch local COVID rate information for given UK postcode."))
    parser.add_argument('postcode')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    html = urlopen(url + quote_plus(args.postcode))
    soup: BeautifulSoup = BeautifulSoup(html, 'lxml')
    tags: ResultSet = soup.find_all('strong')
    x: Tag
    for x in tags:
        if "Rate per 100k" in x.parent.text:
            print(x.text)
            break
