from huobi.client.generic import *
from huobi.client.market import *
from huobi.constant.definition import *
from huobi.exception.huobi_api_exception import *
import asyncio
import requests
import threading


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


def rest_get_trades(p, s_dict):
    market_client = MarketClient()

    coin_name = reformat_crypto_name(p, s_dict)

    try:
        # get history of trades of certain cryptocoin
        res = market_client.get_history_trade(p, 50)

        # print the needed output in a certain format
        for element in res:
            print('!', element.ts,
                  'huobi', coin_name,
                  str(element.direction)[:1].upper(), str('{0:.9f}'.format(element.price)),
                  str('{0:.4f}'.format(element.amount)))
    except HuobiApiException:
        # handle errors
        print(f'Trades for coin {coin_name} can`t be found')


def trade(symbol_dict, list_pairs):
    # create trades for each cryptocoin symbol
    for i in range(len(list_pairs)):
        rest_get_trades(list_pairs[i], symbol_dict)


def order(symbol_dict, list_pairs):
    for symb in list_pairs:
        sdk_get_orders(symb, 500, symbol_dict)


def delta(symbol_dict, list_pairs):
    for symb in list_pairs:
        asyncio.run(rest_get_deltas(symb, 'step0', symbol_dict))


async def rest_get_deltas(symbol_pair, level, s_dict):
    url = f'https://api.huobi.pro/market/depth?symbol={symbol_pair}&depth=20&type={level}'

    responseJSON = requests.get(url)
    response = responseJSON.json()
    if response['status'] == 'error':
        print(f"No deltas available for symbol {reformat_crypto_name(symbol_pair, s_dict)}")
        return
    answer = ''
    answer += '$ ' + str(response['ts']) + ' huobi ' + reformat_crypto_name(symbol_pair, s_dict) + ' B' + ' '
    for elem in response['tick']['bids']:
        answer += str(elem[1]) + '@' + str('{0:.8f}'.format(elem[0])) + ' | '
    answer = answer[:-2]
    print(answer)

    answer = ''
    answer += '$ ' + str(response['ts']) + ' huobi ' + reformat_crypto_name(symbol_pair, s_dict) + ' S' + ' '
    for elem in response['tick']['asks']:
        answer += str(elem[1]) + '@' + str('{0:.8f}'.format(elem[0])) + ' | '
    answer = answer[:-2]
    print(answer)


def sdk_get_orders(symbol, depth, s_dict):
    market_client = MarketClient()

    try:
        order_book = market_client.get_pricedepth(symbol, DepthStep.STEP0, depth)
        answer = ''
        answer += '$ ' + str(order_book.ts) + ' huobi ' + reformat_crypto_name(symbol, s_dict) + ' B' + ' '
        for i in range(len(order_book.bids)):
            answer += str(order_book.bids[i].amount) + '@' + str('{0:.8f}'.format(order_book.bids[i].price)) + ' | '
        answer = answer[:-2] + 'R'
        print(answer)

        answer = ''
        answer += '$ ' + str(order_book.ts) + ' huobi ' + reformat_crypto_name(symbol, s_dict) + ' S' + ' '
        for i in range(len(order_book.asks)):
            answer += str(order_book.asks[i].amount) + '@' + str('{0:.8f}'.format(order_book.asks[i].price)) + ' | '
        answer = answer[:-2] + 'R'
        print(answer)
    except HuobiApiException:
        print(f"No order book available for symbol {reformat_crypto_name(symbol, s_dict)}")


def main():
    # get all cryptocoin symbols
    generic_client = GenericClient()
    list_obj = generic_client.get_exchange_symbols()
    list_pairs = list()
    for elem in list_obj:
        list_pairs.append(elem.symbol)

    # get all pairs of base and quote currencies to check while creating trades
    general_client = GenericClient()
    symbol_pairs = general_client.get_exchange_symbols()
    symbol_dict = dict()
    for i in range(len(symbol_pairs)):
        symbol_dict[symbol_pairs[i].quote_currency] = symbol_pairs[i].base_currency

    t1 = threading.Thread(target=trade, args=(symbol_dict, list_pairs))
    t2 = threading.Thread(target=order, args=(symbol_dict, list_pairs))
    t3 = threading.Thread(target=delta, args=(symbol_dict, list_pairs))
    while True:
        t1.start()
        t2.start()
        t3.start()


    # trade(symbol_dict, list_pairs)
    # order(symbol_dict, list_pairs)
    # delta(symbol_dict, list_pairs)


if __name__ == '__main__':
    main()
