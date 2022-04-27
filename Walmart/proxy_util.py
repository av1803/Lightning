import requests

from Walmart.server_util import get_proxy
from Walmart.util import date_time


def setup_proxy(s: requests.Session):
    """
    Gets a proxy from the server and sets it as the proxy.
    """
    try:
        https_proxy = "http://" + get_proxy(s)
        proxy_dict = {
            "http": https_proxy,
            "https": https_proxy,
        }
        s.proxies.update(proxy_dict)
        print(date_time() + "set proxy to: " + str(s.proxies))
    except Exception:
        print(date_time() + 'error setting proxy')
