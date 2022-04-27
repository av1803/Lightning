import time
from os.path import expanduser

from flask import Flask, request

app = Flask(__name__)
value = False
url = ''
proxy_id = 0
proxies = []
items = []
expiry_time = -1
file = expanduser("~") + 'proxylist.txt'
file2 = expanduser("~") + 'items.txt'


def loadItems(array: [], filepath):
    with open(filepath) as f:
        lines = f.readlines()
        for line in lines:
            res = {}
            res['id'] = line.replace('\n', '');
            res['skuId'] = line.replace('\n', '');
            array.append(res)


def loadProxies(array: [], filepath):
    with open(filepath) as f:
        lines = f.readlines()
        for line in lines:
            array.append(line.replace('\n', ''))


@app.route('/value', methods=['GET'])
def output_value():
    global value
    global expiry_time
    if value:
        if time.time() < expiry_time:
            value = True
        else:
            items.clear()
            expiry_time = -1
            value = False
    return {'value': value, 'expiry': expiry_time}


@app.route('/items', methods=['GET'])
def output_items():
    val = {"items": items}
    return val


@app.route('/url', methods=['GET'])
def output_url():
    if len(url) > 0:
        return url


@app.route('/proxy', methods=['GET'])
def return_proxy():
    global proxy_id
    value = str(proxies[proxy_id])
    proxy_id += 1
    return value


@app.route('/url', methods=['POST'])
def update_url():
    tt = request.get_json(force=True)
    val = tt['url']
    data = str(val)
    print(data)
    global url
    url = data
    return "success"


@app.route('/value', methods=['POST'])
def update_value():
    tt = request.get_json(force=True)
    val = tt['value']
    global value
    value = val

    global expiry_time
    expiry_time = tt['expiry']

    return "success"


@app.route('/item/remove', methods=['POST'])
def remove_item():
    tt = request.get_json(force=True)
    val = tt['id']
    data = str(val)
    if data in items:
        items.remove(data)
    return "success"


@app.route('/item/add', methods=['POST'])
def add_item():
    tt = request.get_json(force=True)
    val = tt['id']
    data = str(val)
    if data in items:
        items.remove(data)
    items.insert(0, data)
    return "success"


@app.route('/item/add_multiple', methods=['POST'])
def add_items():
    tt = request.get_json(force=True)

    for product in tt['items']:
        if product in items:
            items.remove(product)
        items.insert(0, product)

    return "success"


if __name__ == '__main__':
    loadProxies(proxies, file)
    app.run(host='0.0.0.0', port='8080')
