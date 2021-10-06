import re
import requests
from typing import Dict, Optional


class NASAPI(object):

    DEFAULT_TIMEOUT_IN_SECONDS = 5
    DEFAULT_USERNAME = "admin"

    regexps = {
        'sid': r'name="gSSS"\s*value="([0-9a-f]*)"',
        'key': r'name="gRRR"\s*value="([0-9]*)"',
        'used': r'class="content30_2_2">([0-9.]+)&nbsp;GB',
        'total': r'GB&nbsp;/&nbsp;([0-9.]+)&nbsp;GB',
        'url': r'cgi-bin/top\.cgi$',
    }

    def __init__(self,
                 nas_url: str,
                 password: str,
                 timeout: int = DEFAULT_TIMEOUT_IN_SECONDS,
                 user: str = DEFAULT_USERNAME):
        self.nas_url = self.__check_url(nas_url)
        self.password = password
        self.timeout = timeout
        self.user = user
        self.key: Optional[str] = None
        self.sid: Optional[str] = None
        self.sid = self.create_session()

    # TODO: Add __del__ method to log out of NAS (if not shutting down)

    def __check_url(self, url: str) -> str:
        if 'url' in self.regexps:
            if re.search(self.regexps['url'], url):
                return url
        return url + '/cgi-bin/top.cgi'

    def __find_value(self, name: str, text: str) -> Optional[str]:
        if name in self.regexps:
            result = re.search(self.regexps[name], text)
            if result is not None:
                return result.groups()[0]
        return None

    def call(self, params: Dict[str, str]) -> str:
        params.update({
            'gSSS': self.sid or '',
            'gRRR': self.key or '',
            'txtHelpSearch': '',
            'gKey': '',
            'hiddenDummyText': 'dummy',
        })
        # print(params)
        result = requests.post(self.nas_url, params, timeout=self.timeout)
        self.key = self.__find_value('key', result.text)
        return result.text

    def create_session(self) -> Optional[str]:
        try:
            result = self.call({
                'txtAuthLoginUser': self.user,
                'txtAuthLoginPassword': self.password,
                'gPage': 'top',
                'gMode': 'auth',
                'gType': '',
            })
            return self.__find_value('sid', result)

        except requests.exceptions.Timeout:
            raise TimeoutError("NASAPI could not get a response from %s"
                               % self.nas_url)
        except requests.exceptions.RequestException:
            raise ConnectionError("NASAPI could not connect to %s"
                               % self.nas_url)

    def shutdown(self) -> bool:
        result = self.call({
            'gPage': 'maintenance',
            'gMode': 'shutdown',
            'gType': 'shutdown',
        })
        # TODO: Check status OK
        return True

    def restart(self) -> bool:
        result = self.call({
            'gPage': 'maintenance',
            'gMode': 'shutdown',
            'gType': 'reboot',
        })
        # TODO: Check status OK
        return True

    @property
    def capacity(self) -> Dict[str, float]:
        ret: Dict[str, float] = {}
        result = self.call({
                'gPage': 'top',
        })
        used = self.__find_value('used', result)
        total = self.__find_value('total', result)
        if used is not None:
            ret['used'] = float(used)
        if total is not None:
            ret['total'] = float(total)
        if 'used' in ret and 'total' in ret:
            ret['percent_free'] = (100 * (ret['total'] - ret['used'])
                                   / ret['total'])
            ret['percent_used'] = 100 * ret['used'] / ret['total']
            ret['free'] = ret['total'] - ret['used']
        return ret
