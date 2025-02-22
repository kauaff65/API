import requests
from json import dumps, load
from os import path, environ


class Login:
    BASE_URL = 'https://oauth.telegram.org/auth/get'
    LOGIN_URL = 'https://shop.uquid.com/public/tlg/telegramLogin'
    SESSION_FILE = 'Session.json'
    TELEGRAM_FILE = 'Telegram.json'
    TIMEOUT = 60

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://shop.uquid.com/',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://shop.uquid.com',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    def __init__(self):
        self.session = requests.Session()
        self.bot_id = '7179981001'
        if path.exists(self.TELEGRAM_FILE):
            with open(self.TELEGRAM_FILE, 'r') as f:
                self.session.cookies.update(load(f))
        self.session.headers.update(self.HEADERS)


    def fetch_user_data(self):
        params = {'bot_id': self.bot_id}
        data = {'origin': "https://shop.uquid.com"}
        response = self.session.post(self.BASE_URL, params=params, data=data, timeout=self.TIMEOUT)
        response.raise_for_status()
        user_data = response.json().get('user')
        return user_data

    def login(self, user_data):
        if not user_data:
            raise ValueError("Failed to retrieve user data.")
        login_response = self.session.post(self.LOGIN_URL, data=user_data, timeout=self.TIMEOUT)
        login_response.raise_for_status()
        return self.session

    def Login(self):
        try:
            user_data = self.fetch_user_data()
            self.login(user_data)
            environ["Cookies"]  = dumps(self.session.cookies.get_dict(domain=".shop.uquid.com"))
        except :
            raise
