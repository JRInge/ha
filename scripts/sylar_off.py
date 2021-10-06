#!/srv/homeassistant/bin/python3

from argparse import ArgumentParser, Namespace
from nasapi import NASAPI


def get_args() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        description=("Shut down Buffalo NAS"))
    parser.add_argument(
        'host',
        help=("Host name for NAS"))
    parser.add_argument(
        'password',
        help=("Admin password"))
    return parser.parse_args()


def shutdown_nas(url: str, password: str) -> None:
    print('Shutting down NAS at %s: ' % url, end='')
    try:
        nas = NASAPI(url, password)
        if nas.shutdown():
            print('[OK]')
        else:
            print('[Failed]')
    except TimeoutError:
        print('[No response]')
    except ConnectionError:
        print("[Can't connect]")

if __name__ == '__main__':
    args = get_args()
    shutdown_nas(f'http://{args.host}/', args.password)
