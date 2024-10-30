import okx.PublicData as PublicData
import okx.MarketData as MarketData
import okx.Trade as Trade
import okx.Funding as Funding
import okx.Account as Account
from key import *
from util import *



flag = "0"  # live trading: 0, demo trading: 1

PublicDataAPI = PublicData.PublicAPI(flag=flag)
accountAPI    = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
fundingAPI    = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
marketDataAPI = MarketData.MarketAPI(flag = flag)
tradeAPI      = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag)


def get_current_system_time(ms = 0, int_value = 0):
    result = PublicDataAPI.get_system_time()
    data = get_valid_data(result)
    data_0 = data[0]
    ts = data_0['ts']
    return change_time_type(ts, ms=ms, int_value=int_value)


def get_account():
    result = accountAPI.get_account_balance()
    print(result)

def get_avail_funds():
    result = fundingAPI.get_currencies()
    print(result) 

def get_swap_market_data():    
    result = marketDataAPI.get_tickers(instType = "SWAP")
    return result

def get_public_data():
    result = PublicDataAPI.get_instruments(
        instType="SPOT"
        )
    print(result)

def get_trade_data():
    result = tradeAPI.get_fills()
    return result

def get_all_swap_current_price():
    market_result = get_swap_market_data()
    # print(market_result)
    data_list = get_valid_data(market_result)
    return data_list

def get_k_line_piece(coin, end_time, interval, data_num = 300): ## data_num max is 300
    offset = 0
    if interval == "1m":
        offset = 60 * 1000
    elif interval == "15m":
        offset = 15 * 60 * 1000

    ## 交易产品k线数据
    result = marketDataAPI.get_candlesticks( ##  limit:40/2s  100num/time
        before= str(end_time - data_num * offset), 
        after = str(end_time),
        bar   = interval,      
        limit = str(data_num),
        instId=coin+"-USDT-SWAP"
    )
    return result

def get_k_line(coin, interval, num=1): ## 1m 3m 5m 15m 30m 1H 2H 4H
    full_k_line = []
    cur_time = get_current_system_time(ms=1, int_value=1)
    offset   = 0
    min_1m_300_data = 60 * 1000  * 300
    if interval == "1m":
        offset = 1 * min_1m_300_data
    elif interval == "15m":
        offset = 15 * min_1m_300_data

    for i in range(num): # once: num * coin_type_num
        k_line_piece = get_k_line_piece(coin, cur_time - i * offset, interval)
        data = get_valid_data(k_line_piece)
        # print(i, data)
        full_k_line += data
        if ((i % 39) == 38):
            time.sleep(2)
        else:
            pass

    return full_k_line


def get_history_k_line_piece(coin, end_time, interval, data_num = 100): ## data_num max is 300
    offset = 0
    if interval == "1s":
        offset = 1000
    elif interval == "1m":
        offset = 60 * 1000
    elif interval == "15m":
        offset = 15 * 60 * 1000

    ## 交易产品k线数据
    result = marketDataAPI.get_history_candlesticks( ##  limit:40/2s  100num/time
        before= str(int(end_time) - data_num * offset), 
        after = str(int(end_time)),
        bar   = interval,
        limit = str(data_num),
        instId=coin+"-USDT-SWAP"
    )
    return result

def get_history_k_line(coin, interval, num=1): ## 1s 1m 3m 5m 15m 30m 1H 2H 4H
    full_k_line = []
    cur_time = get_current_system_time(ms=1, int_value=1)
    offset   = 0
    min_1m_100_data = 60 * 1000  * 100
    if interval == "1s":
        offset = 1 * min_1m_100_data / 60
    elif interval == "1m":
        offset = 1 * min_1m_100_data
    elif interval == "15m":
        offset = 15 * min_1m_100_data

    for i in range(num): # once: num * coin_type_num
        k_line_piece = get_history_k_line_piece(coin, cur_time - i * offset, interval)
        data = get_valid_data(k_line_piece)
        # print(i, data)
        full_k_line += data
        if ((i % 20) == 19):
            time.sleep(2)
        else:
            pass

    return full_k_line



def get_unfinish_order(): ## not include stop-order
    result = tradeAPI.get_order_list()
    data = get_valid_data(result)
    return data


def get_current_positions():
    result = accountAPI.get_positions()
    data = get_valid_data(result)
    return data

def get_fills():
    result = tradeAPI.get_fills()
    data = get_valid_data(result)
    return data


def set_leverage(coin, lever):
    accountAPI.set_leverage(
        instId = coin,
        lever  = str(lever),
        mgnMode= "isolated"
    )

def get_basic_info():
    result = PublicDataAPI.get_instruments(instType="SWAP")
    data = get_valid_data(result)
    return data

def get_all_swap_list():
    swap_list = []
    for i in get_basic_info():
        if "-USDT-SWAP" in i["instId"]:
            coin_name = i["instId"].split("-")[0]
            swap_list.append(coin_name)
    return swap_list
