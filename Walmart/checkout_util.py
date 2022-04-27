import json

import requests

from Walmart.util import date_time


def initiate_checkout(product_ids: [], price: str, s: requests.Session):
    """
    Initiates the checkout using a list of products, total price, and a request session.

    :param product_ids
        List of product ids
    :param price
        Total price of the cart
    :param s
        The current request session

    :returns a list with payment information, store id, and postal code stored on the account
    """
    payload = {
        "productIds": product_ids,
        "cartSubTotal": price
    }
    s.cookies['walmart.id'] = '579b096d-4ebf-4e4c-84e7-1836e5bd0980'

    tracking = 'https://www.walmart.ca/api/cart-page/cart/rr-tracking'
    post = s.post(url=tracking, json=payload)

    print(date_time() + post.text)

    url = 'https://www.walmart.ca/api/checkout-page/checkout?lang=en&availStoreId=?&postalCode=?&localStoreId' \
          '=?'
    resp = s.get(url, headers=s.headers, cookies=s.cookies)
    print(date_time() + resp.text)
    jason = json.loads(resp.text)
    store_id = jason['localizedInfo']['localStoreId']
    postal = jason['localizedInfo']['postalCode']
    return [jason['paymentInfo'][0]['paymentId'], store_id, postal]


def place_order(store_id: str, postal_code: str, s: requests.Session):
    """
    Sends a checkout (POST) request to the server

    :param store_id
        The store id we are purchasing from
    :param postal_code
        The shipping postal code
    :param s
        The current request session

    """
    load = {
        "cvv": [],
    }
    url = 'https://www.walmart.ca/api/checkout-page/checkout/place-order?lang=en&availStoreId=' + store_id + '&postalCode=' + postal_code
    s.post(url, json=load, cookies=s.cookies, headers=s.headers)
    print(date_time() + 'Potentially bought item, sleeping')
