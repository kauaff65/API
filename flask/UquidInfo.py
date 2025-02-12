import concurrent.futures
from os import getenv
from json import dumps, loads
from requests import Session
from bs4 import BeautifulSoup


class UquidOrders:
    BASE_URL = "https://shop.uquid.com/myaccount/"
    SESSION_FILE = 'Session.json'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://shop.uquid.com/?_c=',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=0',
    }
    def __init__(self):
        cookies = getenv('Cookies')
        if cookies is not None:
            self.cookies = loads(getenv('Cookies'))

    def _create_session(self):
        session = Session()
        session.headers.update(self.HEADERS)
        if self.cookies:
            session.cookies.update(self.cookies)
        return session


    def fetch_balance(self):
        session = self._create_session()
        response = session.get(self.BASE_URL, params={'tab': 'wallet'})
        soup = BeautifulSoup(response.content, 'html.parser')
        usdt_row = soup.find('tr', {'data-symbol': 'USDT'})
        if usdt_row:
            balance_span = usdt_row.find('span', {'style': 'color:green;font-weight: bold'})
            if balance_span:
                return balance_span.text.strip()
            elif usdt_row.get('data-value'):
                return usdt_row.get('data-value')
        return "Balance not found"

    def fetch_orders_page(self):
        session = self._create_session()
        response = session.get(
            self.BASE_URL,
            params={'tab': 'order', 'tv': 'QmNzjIhpDMPT', 't': 'xuztLEcV'}
        )
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.content, 'html.parser')
        if soup.find('td', class_='trn', string="There is no item available"):
            return []

        table = soup.find('table', {'class': 'table'})
        if not table:
            return []

        orders = []
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if len(cols) == 2:
                order_col = cols[1]
                order_details = {
                    'order_name': order_col.find('a').text.strip() if order_col.find('a') else None,
                    'quantity_price': order_col.find_all('div')[1].text.strip() if len(order_col.find_all('div')) > 1 else None,
                    'usdt_amount': order_col.find_all('div')[2].text.strip() if len(order_col.find_all('div')) > 2 else None,
                    'order_id': order_col.find_all('div')[3].text.strip() if len(order_col.find_all('div')) > 3 else None,
                    'batch_id': order_col.find_all('div')[4].text.replace("\n", "").replace(" ", "").replace("BatchID:", "").strip() if len(order_col.find_all('div')) > 4 else None,
                    'execution_status': order_col.find_all('div')[5].text.replace("\n", "").replace(" ", "").replace("Execution:", "").strip() if len(order_col.find_all('div')) > 5 else None,
                    'payment_status': order_col.find_all('div')[6].text.replace("\n", "").replace(" ", "").replace("Payment:", "").strip() if len(order_col.find_all('div')) > 6 else None,
                    'order_date': order_col.find_all('div')[7].text.strip() if len(order_col.find_all('div')) > 7 else None,
                }
                orders.append(order_details)
        return orders

    def fetch_data(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_balance = executor.submit(self.fetch_balance)
            future_orders = executor.submit(self.fetch_orders_page)
            balance = future_balance.result()
            orders = future_orders.result()

        data = {
            'balance': balance,
            'orders': orders
        }
        return dumps(data, indent=4)

