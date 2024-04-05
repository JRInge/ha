import asyncio
from afsapi import AFSAPI


def get_rssi():
    fs = AFSAPI('http://kitchen-radio.local/device', '1234')

    rssi = yield from fs.handle_int('netRemote.sys.net.wlan.rssi')
    print(rssi)

LOOP = asyncio.get_event_loop()
LOOP.run_until_complete(get_rssi())
LOOP.close()
