import json
import time
import numpy as np


def log_info(log, file_path, keep_cur_line=0):
    with open(file_path, "a+") as f:
        f.write(log)
        if keep_cur_line:
            pass
        else:
            f.write("\n")

def get_valid_data(result):
    if result["code"] == '0':
        return result['data']
    elif result["code"] == '51001':
        print("交易产品id不存在")
    else:
        print("返回数据无效")
        print(str(result))

def get_second_from_ms(ts):
    return ts[:-3]

def change_time_type(ts, ms = 0, int_value = 0):
    if int_value == 1:
        if ms == 1:
            result = int(ts)
            return result
        else:
            return int(get_second_from_ms(ts))
    else:
        if ms == 1:
            return ts
        else:
            return get_second_from_ms(ts)
        
def price_can_trade(price, k_history_piece):
    cur_highest = float(k_history_piece[2])
    cur_lowest  = float(k_history_piece[3])
    price = float(price)
    if (price <= cur_highest) and (price >= cur_lowest):
        return 1
    else:
        return 0


def get_config():
    with open("./config/coins.json", "r") as f:
        config = json.load(f)[0]
    return config

def time_flag_per_minite(cur_ctime, flag_15m = 1):
    cur_clock_str = cur_ctime.split(" ")[-2]
    cur_sec = cur_clock_str[-2:]
    cur_min = cur_clock_str[-5:-3]
    cur_sec_int = int(cur_sec)
    cur_min_int = int(cur_min)

    if flag_15m:
        wait_min = 15 - cur_min_int%15 -1
        time.sleep(wait_min * 60)

    time.sleep(60 - cur_sec_int)

    time.sleep(1) ## wait 1s to get newest complete data

    if cur_min == "14" or cur_min == "29" or cur_min == "44" or cur_min == "59":
        return 2
    else:
        return 1

def get_variance(ls):
    newest = ls[-1]
    percent_list = []
    for i in ls:
        percent = i/newest
        percent_list.append(percent)
    return np.var(percent_list) * 100 / 2

## return [x^n, ... , x^1, x^0]
def polyfit(ls, n):
    x = range(len(ls))
    return np.polyfit(x, ls, n)