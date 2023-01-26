# huobi-fetcher
https://www.huobi.com/en-us/

Fetcher for huobi crypto exchange to get trades, order books and deltas for all available crypto symbols

Functions trade, order and delta call other functions to achieve certain data

Function rest_get_delta uses rest api to get all needed deltas(max 20 positions of sell/buy orders)

Function rest_get_trades uses sdk function(while sdk function uses rest api), to get all the needed trades(history of trades for this particular symbol)

Function sdk_get_orders uses sdk function(while sdk function uses rest api), to get max of 500 positions of buy/sell orders for certain symbol

Function reformat_crypto_name is used to reformat symbol name from ex. 'btcusdt' to 'BTC-USDT'

You need to launch file fetcher.py
