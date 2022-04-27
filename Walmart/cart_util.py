import json
import pprint
import sys
from datetime import time
from random import random

import requests

from Walmart.util import date_time, is_blocked


def build_item(item: {}):
    """
    Builds a dictionary for the given item.

    :param item
        The item to be built.

    :returns The item dictionary
    """
    item_id = item['id']
    sku_id = item['sku_id']
    if item_id[0] != "P":
        try:
            item_id = str(int(item_id) + 1)
        except Exception:
            item_id = str(item_id)
    else:
        item_id = str(item_id).replace("PRD", "")
        sku_id = item_id

    print(item_id)
    val = {'offerId': item_id, 'sku_id': sku_id, 'quantity': "1", 'allowSubstitutions': 'false',
           'subscription': 'false', 'action': 'UPDATE'}

    return val


def build_items(item_list: [], s: requests.Session):
    """
    Builds a list for the given items.

    :param item_list
        The list of items to be built.
    :param s
        The current request session.

    :returns The list of built items
    """
    items = []
    for item_id in item_list:
        stock = in_stock(item_id, s)
        time.sleep(random.randint(2, 3))
        if stock is None:
            continue
        if isinstance(stock[0], bool) and stock[0]:
            try:
                item_id = str(int(item_id) + 1)
            except Exception:
                item_id = str(item_id)
            val = {'offerId': item_id, 'skuId': stock[1], 'quantity': "1", 'allowSubstitutions': 'false',
                   'subscription': 'false', 'action': 'UPDATE'}
            items.append(val)

    return items


def add_to_cart(item_ids: [], s: requests.Session):
    """
    Adds a list of given items to the cart.

    :param item_ids
        The list of items to be added.
    :param s
        The current request session.

    :returns The price of the items (combined) and the list of added items
    """
    req = {
        "postalCode": "",
        "items": build_items(item_ids, s),
        "pricingStoreId": ""
    }
    data = json.dumps(req)
    print("adding items to cart: ")

    s.headers['referer'] = 'https://www.walmart.ca/search?q=ps5+console&c=10012'

    pp = s.post('https://www.walmart.ca/api/home-page/cart?responseGroup=full&storeId=?&lang=en',
                json=data, headers=s.headers, cookies=s.cookies, allow_redirects=True)

    if is_blocked(pp.text):
        print('blocked from adding to cart')
    print(pp.text)
    try:
        if pp.text.find('error') != -1:
            print('error')
            time.sleep(random.randint(1, 3))
            add_to_cart(item_ids, s)
        else:
            table = json.loads(pp.text)
            price = table['cartPriceInfo']['subTotal']
            items = table['items']['allIds']
            return [price, items]
    except Exception:
        return False


def add_to_cart2(li: [], s: requests.Session):
    """
    Adds a list of given items to the cart.

    :param item_ids
        The list of items to be added.
    :param s
        The current request session.

    :returns The price of the items (combined) and the list of added items
    """
    if len(li) == 0:
        return False
    s.headers['referer'] = 'https://www.walmart.ca/search?q=ps5+console&c=10012'

    current_price = 0
    success = 0
    successful_items = []
    event_id = s.cookies["DYN_USER_ID"]
    for item in li:
        if len(li) != 0:
            req = {
                "eventId": event_id,
                "postalCode": "",
                "items": [build_item(item)],
                "pricingStoreId": ""
            }
            data = json.dumps(req)
            print(date_time() + "adding items to cart: ", str(item))
            pp = s.post('https://www.walmart.ca/api/home-page/cart?responseGroup=full&storeId=?&lang=en',
                        json=data, headers=s.headers, cookies=s.cookies)

            time.sleep(0.5)

            if is_blocked(pp.text):
                print(date_time() + 'blocked, idling this bot')
                time.sleep(200)

            print(pp.text)
            try:
                if pp.text.find('error') != -1:
                    print(date_time() + 'error in adding to cart')
                else:
                    table = json.loads(pp.text)
                    current_price = table['cartPriceInfo']['subTotal']
                    successful_items = table['items']['allIds']
                    success += 1
                    print(date_time() + 'Successfully added to cart: ' + item['id'])

            except Exception:
                return False

    if success == 0 or current_price == 0:
        print(date_time() + "no items to add")
        return False

    return [current_price, successful_items]


def in_stock(item_id: str, s: requests.Session):
    """
    Checks if an item is stocked.

    :param item_id
        The item to be checked
    :param s
        The current request session.

    :returns a list of 2 values
            value [0] -> a boolean to check if the item is in stock
            value [1] -> the sku id of that item
    """
    url = 'https://www.walmart.ca/en/ip/' + item_id
    try:
        s.headers['referer'] = 'https://www.walmart.ca'
        r = s.get(url, cookies=s.cookies)
        if is_blocked(r.text):
            print(date_time() + 'blocked from checking stock on item, EXITING')
            sys.exit(0)
        else:
            splitted = r.text.split("OnlineStatus")
            cleaned = splitted[1].split("}")[0].replace('"', '').split(":")[1]
            splitted2 = r.text.split('"name":"Price","value":')
            price_range_value = int(splitted2[1].split(' ')[0].replace('"$', ''))
            print(item_id + " " + str(price_range_value))
            idx = r.text.split('activeSkuId":"')[1].split('"')[0].replace('skuId', '')
            gg = cleaned == 'In Stock Online' and price_range_value < 1000
            if gg:
                print(date_time() + "ADDING to cart: " + item_id)
            else:
                print(date_time() + "NOT adding to cart: " + item_id)
            return [gg, idx]
    except Exception:
        print(Exception.with_traceback())
        return [False, False]


cart_url = ''


def print_cart(s: requests.Session):
    """
    Helper function to print the current cart

    :param s
        The current request session.
    """
    text = s.get(
        url=cart_url,
        headers=s.headers,
        cookies=s.cookies)
    pprint.pprint(text.text)
