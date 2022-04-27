import sys
from datetime import time
from time import sleep
import requests

from Walmart.server_util import server_ready, load_items_from_server
from Walmart.util import date_time
from Walmart.buyer import Buyer

#
# Proxy mode default set to true
#
proxy = True


def handleArguments(b: Buyer):
    """
    Checks the system arguments and handles them appropriately

    :param b: Buyer object reference

    Arguments are in the order:
    0 -> empty
    1 -> username
    2 -> password
    3 -> proxy mode (true or false)
    """
    n = len(sys.argv)
    if n >= 3:
        b.login['username'] = sys.argv[1]
        b.login['password'] = sys.argv[2]
    global proxy
    if n >= 4:
        proxy = "true" in sys.argv[3]


if __name__ == '__main__':
    b = Buyer()
    handleArguments(b)
    with requests.Session() as s:
        while True:
            if not server_ready(s):
                print(date_time() + " Waiting for ping from server")
                sleep(1.5)
            else:
                print(date_time() + " Server is ready, initiating purchase")
                load_items_from_server(b, s)
                start = time.time()
                end = start + 120
                try:
                    b.logic(s, end)
                except requests.exceptions.ProxyError:
                    print(date_time() + 'Resetting Proxy')
                    s.proxies.clear()

                s.proxies.clear()
