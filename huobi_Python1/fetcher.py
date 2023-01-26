from huobi.client.generic import *
from huobi.client.market import *
from huobi.constant.definition import *
from huobi.exception.huobi_api_exception import *
import asyncio
import requests
import threading
import gzip
from websockets import connect


def reformat_crypto_name(name, symbol_dictionary):
    # get the name of cryptocoin in the correct format, example before 'btcusdt', after 'BTC-USDT'
    crypto_name = ''
    for i in range(-1, -len(name), -1):
        temp = str(name[i:])
        search_res = symbol_dictionary.get(temp)
        if search_res:
            crypto_name = name[:i].upper() + '-' + name[i:].upper()
            break
    return crypto_name


def rest_get_trades(bc, qc):
    coin_name = bc.upper() + '-' + qc.upper()

    # get history of trades of certain cryptocoin
    trade_url = f"https://api.huobi.pro/market/history/trade?symbol={bc + qc}&size=2000"
    responseJSON = requests.get(trade_url)
    resp = responseJSON.json()
    if resp['status'] != 'ok':
        print(f'Trades for coin {coin_name} can`t be found')
        return

    for elem_out in resp['data']:
        for elem_in in elem_out['data']:
            print('!', elem_in['ts'],
                  'huobi', coin_name,
                  str(elem_in['direction'])[:1].upper(), str('{0:.9f}'.format(elem_in['price'])),
                  str('{0:.4f}'.format(elem_in['amount'])))


def trade(symbol_dict):
    # create trades for each cryptocoin symbol
    for key, value in symbol_dict.items():
        rest_get_trades(key, value)


def order(symbol_dict):
    for key, value in symbol_dict.items():
        sdk_get_orders(key, value)


def delta(symbol_dict):
    for key, value in symbol_dict.items():
        rest_get_deltas(key, value)


def rest_get_deltas(bc, qc):
    delta_url = f'https://api.huobi.pro/market/depth?symbol={bc+qc}&depth=20&type=step0'

    responseJSON = requests.get(delta_url)
    response = responseJSON.json()
    if response['status'] != 'ok':
        print(f"No deltas available for symbol {bc.upper() + '-' + qc.upper()}")
        return
    answer = ''
    answer += '$ ' + str(response['ts']) + ' huobi ' + bc.upper() + '-' + qc.upper() + ' B' + ' '
    for elem in response['tick']['bids']:
        answer += str(elem[1]) + '@' + str('{0:.8f}'.format(elem[0])) + ' | '
    answer = answer[:-2]
    # print(answer)

    answer += '\n'
    answer += '$ ' + str(response['ts']) + ' huobi ' + bc.upper() + '-' + qc.upper() + ' S' + ' '
    for elem in response['tick']['asks']:
        answer += str(elem[1]) + '@' + str('{0:.8f}'.format(elem[0])) + ' | '
    answer = answer[:-2]
    print(answer)


def sdk_get_orders(bc, qc):
    order_url = f'https://api.huobi.pro/market/depth?symbol={bc + qc}&type=step0'

    responseJSON = requests.get(order_url)
    response = responseJSON.json()
    if response['status'] != 'ok':
        print(f"No deltas available for symbol {bc.upper() + '-' + qc.upper()}")
        return
    answer = ''
    answer += '$ ' + str(response['ts']) + ' huobi ' + bc.upper() + '-' + qc.upper() + ' B' + ' '
    for elem in response['tick']['bids']:
        answer += str(elem[1]) + '@' + str('{0:.8f}'.format(elem[0])) + ' | '
    answer = answer[:-2] +'R'
    #print(answer)

    answer += '\n'
    answer += '$ ' + str(response['ts']) + ' huobi ' + bc.upper() + '-' + qc.upper() + ' S' + ' '
    for elem in response['tick']['asks']:
        answer += str(elem[1]) + '@' + str('{0:.8f}'.format(elem[0])) + ' | '
    answer = answer[:-2] +'R'
    print(answer)


def main():
    # get all cryptocoin symbols
    currency_url = 'https://api.huobi.pro/v1/settings/common/market-symbols'
    curr_response = requests.get(currency_url)
    resp = curr_response.json()
    list_symbols = list()
    for i in range(len(resp['data'])):
        list_symbols.append(resp['data'][i]['symbol'])

    # get all pairs of base and quote currencies to check while creating trades
    symbol_dict = dict()
    for i in range(len(resp['data'])):
        symbol_dict[resp['data'][i]['bc']] = resp['data'][i]['qc']

    t1 = threading.Thread(target=trade, args=(symbol_dict,))
    t2 = threading.Thread(target=order, args=(symbol_dict,))
    t3 = threading.Thread(target=delta, args=(symbol_dict,))

    t1.start()
    t2.start()
    t3.start()


    # trade(symbol_dict, list_pairs)
    # order(symbol_dict, list_pairs)
    # delta(symbol_dict, list_pairs)


if __name__ == '__main__':
    main()
