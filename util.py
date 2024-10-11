import json

def log_info(log, keep_cur_line=0):
    with open("run.log", "a+") as f:
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
    if price <= cur_highest and price >= cur_lowest:
        return 1
    else:
        return 0


def get_config():
    with open("coins.json", "r") as f:
        config = json.load(f)[0]
    return config