import logging
import requests
from json import dumps, load
from os import path, environ
import base64


class Login:
    BASE_URL = 'https://oauth.telegram.org/auth/get'
    LOGIN_URL = 'https://shop.uquid.com/public/tlg/telegramLogin'
    SESSION_FILE = 'Session.json'
    TELEGRAM_FILE = 'Telegram.json'
    TIMEOUT = 30

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
        self._setup_logger()

    def _setup_logger(self):
        self.logger = logging.getLogger("LoginLogger")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            # File handler
            file_handler = logging.FileHandler('main.log', mode='a')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        self.logger.propagate = False

    def fetch_user_data(self):
        self.logger.info("Fetching user data from %s", self.BASE_URL)
        params = {'bot_id': self.bot_id}
        data = {'origin': "https://shop.uquid.com"}
        response = self.session.post(self.BASE_URL, params=params, data=data, timeout=self.TIMEOUT)
        response.raise_for_status()
        user_data = response.json().get('user')
        self.logger.info("Fetched user data: %s", user_data)
        return user_data

    def login(self, user_data):
        if not user_data:
            self.logger.error("Failed to retrieve user data.")
            raise ValueError("Failed to retrieve user data.")
        self.logger.info("Logging in using user data...")
        login_response = self.session.post(self.LOGIN_URL, data=user_data, timeout=self.TIMEOUT)
        login_response.raise_for_status()
        self.logger.info("Login successful.")
        return self.session

    def Login(self):
        try:
            user_data = self.fetch_user_data()
            self.login(user_data)
            cookies_dict = self.session.cookies.get_dict(domain=".shop.uquid.com")
            encoded_cookies = base64.b64encode(dumps(cookies_dict).encode()).decode()
            environ["Cookies"] = encoded_cookies
            # environ["Cookies"] = dumps(self.session.cookies.get_dict(domain=".shop.uquid.com"))
        except Exception as e:
            self.logger.error("Error during login process: %s", str(e))
            raise
