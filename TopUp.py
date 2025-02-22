import requests
from re import search
from bs4 import BeautifulSoup
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from os import getenv
from json import loads
# Set your Telegram bot token and chat ID here

TELEGRAM_BOT_TOKEN = "7938248812:AAF31sW-6EJGAZFggDaCa3EEBfu-2mKzC-g"
TELEGRAM_CHAT_ID = "5653451533"
class TelegramHandler(logging.Handler):
    """
    A logging handler that sends log messages to a Telegram chat.
    """
    def __init__(self, token, chat_id, level=logging.NOTSET):
        super().__init__(level)
        self.token = token
        self.chat_id = chat_id

    def emit(self, record):
        try:
            msg = self.format(record)
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {"chat_id": self.chat_id, "text": msg}
            # Send the log message via a POST request
            requests.post(url, data=data, timeout=5)
        except Exception:
            self.handleError(record)

class Uquid:
    SESSION_FILE = 'Session.json'
    def __init__(self, destination_number, value):
        self.destination_number = destination_number
        self.value = str(value)
        self.checkouttoken = None
        self.session = requests.Session()
        cookies = getenv('Cookies')
        if cookies is not None:
            self.session.cookies.update(loads(cookies))
        self.base_url = 'https://shop.uquid.com/topup'
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        self._setup_logger()

    def _setup_logger(self):
        """
        Embed the logger inside the object.
        This logger writes to a file, prints to the console, and sends messages to Telegram.
        """
        self.logger = logging.getLogger(f"UquidLogger.{self.destination_number}")
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
            # Telegram handler
            telegram_handler = TelegramHandler(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
            telegram_handler.setLevel(logging.INFO)
            telegram_handler.setFormatter(formatter)
            self.logger.addHandler(telegram_handler)
        self.logger.propagate = False

    def browse_topup(self):
        url = f'{self.base_url}/browse'
        params = {
            'product_id': '',
            'product_type': 'topup',
            'country_id': '729',
            'country_code': 'EG',
            'operator_id': '716'
        }
        self.logger.info("Browsing top-up options...")
        response = self.session.get(url, params=params, headers=self.default_headers)
        response.raise_for_status()
        return response

    def step1(self):
        url = f'{self.base_url}/step1'
        headers = self.default_headers.copy()
        headers.update({
            'Referer': 'https://shop.uquid.com/topup?denomination=200',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://shop.uquid.com',
            'X-Requested-With': 'XMLHttpRequest'
        })
        data = {
            'country': '729',
            'operator': '716',
            'customPlan': '1',
            'custom_denomination_input_val': self.value,
            'custom_denomination': (
                '%7B%22min%22%3A8%2C%22max%22%3A%22200%22%2C%22step%22%3A%221%22'
                '%2C%22decimal%22%3A0%2C%22faceCurrency%22%3A%22EGP%22%7D'
            ),
            'product': 'WQCVrbedPDdWHo',
            'destination_number': self.destination_number,
        }
        self.logger.info("Executing step1...")
        response = self.session.post(url, data=data, headers=headers)
        response.raise_for_status()
        return response

    def step2(self):
        url = f'{self.base_url}/step2/'
        headers = self.default_headers.copy()
        headers.update({
            'Referer': 'https://shop.uquid.com/topup?denomination=200',
            'X-Requested-With': 'XMLHttpRequest'
        })
        params = {
            'product': 'WQCVrbedPDdWHo',
            'destination_number': self.destination_number
        }
        self.logger.info("Executing step2...")
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        match = search(r'data-checkouttoken=\\"(.*?)\\"', response.text)
        if match:
            self.checkouttoken = match.group(1)
            self.logger.info("Checkout token obtained.")
            return self.checkouttoken
        else:
            self.logger.error("Checkout token not found.")
            raise Exception("Checkout token not found.")

    def step3(self):
        url = f'{self.base_url}/step3/USDT'
        headers = self.default_headers.copy()
        headers.update({
            'Referer': 'https://shop.uquid.com/topup?denomination=200',
            'X-Requested-With': 'XMLHttpRequest'
        })
        params = {
            'destination_number': self.destination_number,
            'product': 'WQCVrbedPDdWHo'
        }
        self.logger.info("Executing step3...")
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response

    def step4(self):
        url = f'{self.base_url}/step4/'
        headers = self.default_headers.copy()
        headers.update({
            'Referer': 'https://shop.uquid.com/topup?denomination=200',
            'X-Requested-With': 'XMLHttpRequest'
        })
        params = {
            'destination_number': self.destination_number,
            'product': 'WQCVrbedPDdWHo',
            'symbol': 'USDT',
            'checkoutToken': self.checkouttoken
        }
        self.logger.info("Executing step4...")
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        try:
            response_json = response.json()
            if "html" in response_json:
                soup = BeautifulSoup(response_json["html"], 'lxml')
                result = {
                    "batch_id": soup.find('div', {'data-trn-key': 'LANG-Batch_ID'}).find_next_sibling().text.strip(),
                    "order_creation_status": soup.find('div', {'data-trn-key': 'LANG-Create_Order'}).find_next_sibling().text.strip(),
                    "mobile_number": soup.find('div', {'data-trn-key': 'LANG-Mobile_Number'}).find_next_sibling().text.strip(),
                    "payment_amount": soup.find('div', {'data-trn-key': 'LANG-Payment_Amount'}).find_next_sibling().text.strip(),
                    "charged_amount": f"{self.value} EGP"
                }
                self.logger.info("Step4 completed and parsed successfully.")
                self.logger.info(result)
                return result
        except Exception as e:
            self.logger.error("Failed to parse step4 response: " + str(e))
            raise
        return response

    def run(self):
        """
        Execute the entire top-up process using parallel threads where possible.
        After step1, step2 and step3 run concurrently since they are independent;
        then step4 is executed after step2 (checkout token) is available.
        """
        start_time = time.time()
        self.logger.info("Starting topup process...")
        self.browse_topup()
        self.step1()
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_step2 = executor.submit(self.step2)
            future_step3 = executor.submit(self.step3)
            token = future_step2.result()
            _ = future_step3.result()
        result = self.step4()
        elapsed = time.time() - start_time
        self.logger.info(f"Topup process completed in {elapsed:.2f} seconds.")
        return result
