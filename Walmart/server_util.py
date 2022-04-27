import json

import requests

from Walmart.buyer import Buyer

server_ready_url = ''
server_proxy_url = ''
server_items_url = ''


def server_ready(s: requests.Session):
    """
    Sends a get request to the server to check if the server is ready.

    My server implementation responds with "true"

    :returns a boolean value, true if the server is ready, false otherwise
    """
    try:
        txt = s.get(server_ready_url)
        jason = json.loads(txt.text)
        return txt.status_code == 200 and bool(jason['value'])
    except Exception:
        return False


def get_proxy(s: requests.Session):
    """
    Sends a get request to the server.

    The server returns a valid proxy as a String.

    :returns the proxy as a String
    """
    txt = s.get(server_proxy_url)
    return txt.text.replace(':proxy', "@proxy").replace('\n', '')


def load_items_from_server(b: Buyer, s: requests.Session):
    """
    Sends a get request to the server.

    :returns the list of items stored on the server
    """
    txt = s.get(server_items_url)
    jason = json.loads(txt.text)
    li = jason['items']
    for item in li:
        b.items.append(item)
