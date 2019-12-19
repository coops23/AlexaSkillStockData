import json
import requests
from datetime import datetime
from datetime import timedelta
from yahoo_fin import stock_info as si
import numpy as np

class GlobalQuote:
    def __init__(self, json_output_dict):
        self.symbol = json_output_dict['01. symbol']
        self.open_price = json_output_dict['02. open']
        self.high = json_output_dict['03. high']
        self.low = json_output_dict['04. low']
        self.price = json_output_dict['05. price']
        self.volume = json_output_dict['06. volume']
        self.latest_trading_day = json_output_dict['07. latest trading day']
        self.previous_close = json_output_dict['08. previous close']
        self.change = json_output_dict['09. change']
        self.change_percent = json_output_dict['10. change percent']

    def __str__(self):
        msg = "{'Global Quote':\n "
        msg += "\t{'01. symbol': '" + self.symbol + "',\n "
        msg += "\t'02. open': '" + self.open_price + "',\n "
        msg += "\t'03. high': '" + self.high + "',\n "
        msg += "\t'04. low': '" + self.low + "',\n "
        msg += "\t'05. price': '" + self.price + "',\n "
        msg += "\t'06. volume': '" + self.volume + "',\n "
        msg += "\t'07. latest trading day: '" + self.latest_trading_day + "',\n "
        msg += "\t'08. previous close: " + self.previous_close + "',\n "
        msg += "\t'09. change': '" + self.change + "',\n "
        msg += "\t'10. change percent': '" + self.change_percent + "'\n "
        msg += "\t}\n "
        msg += "} "

        return msg


def get_stock_data_yf(ticker_symbol):
    # yields string like this
    #               open    high          low        close     adjclose   volume ticker
    # 2019-12-16  1767.0  1769.5  1757.050049  1769.209961  1769.209961  3149345   AMZN

    try:
        yesterday = datetime.strftime(datetime.now() - timedelta(1), '%d/%m/%Y')
        today = datetime.strftime(datetime.now() + timedelta(1), '%d/%m/%Y')
        stock_data = si.get_data(ticker_symbol, start_date=yesterday, end_date=today)
        stock_data = stock_data.to_numpy().tolist()

        todays_stock_data = stock_data[1]
        yesterdays_stock_data = stock_data[0]

        previous_close = yesterdays_stock_data[3]
        open = todays_stock_data[0]
        high = todays_stock_data[1]
        low = todays_stock_data[2]
        close = todays_stock_data[3]
        volume = todays_stock_data[5]
        ticker = todays_stock_data[6]

        price = si.get_live_price(ticker_symbol)
        change = float(price) - float(previous_close)
        change_percent = (change / float(open)) * 100

        table = dict()
        table['01. symbol'] = str(ticker)
        table['02. open'] = '%.2f' % open
        table['03. high'] = '%.2f' % high
        table['04. low'] = '%.2f' % low
        table['05. price'] = '%.2f' % price
        table['06. volume'] = str(volume)
        table['07. latest trading day'] = today
        table['08. previous close'] = '%.2f' % previous_close
        table['09. change'] = '%.2f' % change
        table['10. change percent'] = '%.2f percent' % change_percent

        return_status = GlobalQuote(table)
    except AssertionError as e:
        return [False, "Unable to find " + str(ticker_symbol)]
    except ValueError as e:
        return [False, "Unable to find " + str(ticker_symbol)]
    except KeyError as e:
        return [False, "Unable to find " + str(ticker_symbol)]

    return [True, return_status]

def get_stock_data(ticker_symbol):
    base_request_msg = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol="
    api_key_msg = "apikey=WH5MUXZDEE9X3D1U"
    request_msg = base_request_msg + ticker_symbol + "&" + api_key_msg

    return_status = ""
    try:
        response = requests.get(request_msg)
        json_output_dict = json.loads(response.text)
        return_status = GlobalQuote(json_output_dict['Global Quote'])
    except ValueError as e:
        return [False, e]
    except KeyError as e:
        return [False, "Key error for" + str(e)]

    return [True, return_status]


def best_match_data(ticker_symbol):
    base_request_msg = "https://www.alphavantage.co/query?function=SYMBOL_SEARCH&"
    keywords_msg = "keywords=" + ticker_symbol + "&"
    api_key_msg = "apikey=WH5MUXZDEE9X3D1U"
    request_msg = base_request_msg + keywords_msg + api_key_msg

    response = requests.get(request_msg)
    json_output_dict = json.loads(response.text)

    json_output_dict_list = json_output_dict['bestMatches']
    search_option_list = []
    if len(json_output_dict_list) == 0:
        return None

    for output in json_output_dict_list:
        search_option_list.append([output['1. symbol'], output['2. name']])

    return search_option_list

def match_data(ticker_symbol):
    ticker_symbol = ticker_symbol.replace(" ", "")
    ticker_symbol = ticker_symbol.replace(".", "")
    ticker_symbol = ticker_symbol.replace("dot", ".")
    ticker_symbol = ticker_symbol.replace("point", ".")
    ticker_symbol = ticker_symbol.upper()

    return ticker_symbol

def main():
    symbol_ticker = "i. n. t. d."

    symbol_ticker = match_data(symbol_ticker)
    [status, weed_to] = get_stock_data_yf(symbol_ticker)
    if not status:
        print(symbol_ticker + " not found. Seaching for matches.")
        search_option_list = best_match_data(symbol_ticker)
        if search_option_list is not None:
            for search_option in search_option_list:
                print(search_option)
        else:
            print("Sorry, ticker. " + symbol_ticker + " does not exist. Please try something else.")
    else:
        print(weed_to)

    [status, weed_to] = get_stock_data(symbol_ticker)
    if not status:
        print(symbol_ticker + " not found. Searching for matches.")
        search_option_list = best_match_data(symbol_ticker)
        if search_option_list is not None:
            for search_option in search_option_list:
                print(search_option)
        else:
            print("Sorry, ticker. " + symbol_ticker + " does not exist. Please try something else.")
    else:
        print(weed_to)


if __name__ == '__main__':
    main()