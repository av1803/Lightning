import sys
import time
from os.path import expanduser

import requests

from Walmart.cart_util import add_to_cart2
from Walmart.checkout_util import initiate_checkout, place_order
from Walmart.util import is_blocked
from bot import date_time


class Buyer:
    headers = {
        'accept-encoding': 'gzip',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/96.0.4664.45 Safari/537.36',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'origin': 'https://www.walmart.ca',
        'referer': 'https://www.walmart.ca/',
        'sec-fetch-mode': 'cors',
        'sec-feth-dest': 'empty',
        'sec-fetch-site': 'same-origin',
    }
    file = expanduser("~") + 'accounts.txt'
    info = expanduser("~") + 'items.txt'
    items = []
    item_ids = []
    total = ''
    login = {}
    phone = ''
    found = False

    def loadAccountInformation(self, filepath):
        with open(filepath) as f:
            lines = f.readlines()
            for line in lines:
                splitted = line.split(":")
                self.login[0] = (splitted[0])
                self.login[1] = (splitted[1])

    def login(self, s: requests.Session):
        """
        Attempts to login.

        :param self
            This buyer object

        :param s
            The current request session.

        :returns a boolean, true if login successful, false otherwise
        """
        s.headers['referer'] = 'https://www.walmart.ca/sign-in?from=%2Fmy-account'
        text = s.post('https://www.walmart.ca/api/auth-page/login', data=self.login,
                      headers=s.headers, cookies=s.cookies)

        print(text.content)

        if is_blocked(text.text):
            print(date_time() + 'we are blocked from logging in')
            return False

        return True

    def logic(self, s: requests.Session, end: int):
        """
        Main logic of the buyer.

        Attempts to login, if unable to login after 10 attempts the buyer terminates

        If logged in successfully, the buyer attempts to build the cart and execute the checkout process.

        :param self
            This buyer object

        :param s
            The current request session.

        :param end
            How long this method should run for (in seconds)

        """
        s.cookies.clear()
        s.headers.update(self.headers)
        logged_in = self.login()
        i = 0
        while not logged_in:
            s.cookies.clear()
            logged_in = self.login()
            if logged_in:
                break
            else:
                i += 1
                if i > 10:
                    print(date_time() + "Failed too many times, exiting")
                    sys.exit(0)
                time.sleep(2.5)

        s.cookies['WM.USER_STATE'] = 'REGISTERED|Authenticated'
        while time.time() < end:
            vals = add_to_cart2(self, self.items, s)
            if isinstance(vals, bool):
                print(date_time() + 'error, retrying')
                time.sleep(2.5)
            else:
                price = vals[0]
                valid_items = vals[1]
                jason = initiate_checkout(valid_items, str(price), s)
                payment_id = jason[0]
                store_id = jason[1]
                postal = jason[2]
                print(date_time() + 'Placing order')
                place_order(store_id=store_id, postal_code=postal, payment_id=payment_id, s=s)
                time.sleep(120)
