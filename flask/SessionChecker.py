from requests import Session, utils
from os import getenv
import json 
import base64 

class SessionChecker:
    BASE_URL = "https://shop.uquid.com"
    LOGIN_ENDPOINT = "/game/claim_free"
    def __init__(self):
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://shop.uquid.com/game/glt0/',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://shop.uquid.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
    def Check(self):
        cookies = getenv("Cookies")
        if cookies:
            decoded_cookies = json.loads(base64.b64decode(cookies.encode()).decode())
            jar = utils.cookiejar_from_dict(decoded_cookies)
            self.session.cookies.update(jar)
            try:
                response = self.session.post(f'{self.BASE_URL}{self.LOGIN_ENDPOINT}', timeout=10)
                if response.status_code == 200 and "Please login to use this function." not in response.text:
                    return True
                else:
                    return False
            except Exception as e:
                return False
        return False


