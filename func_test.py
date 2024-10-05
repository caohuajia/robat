import time
import json
from base_okx import *
from pub_test import *

def get_basic_info():
    result = PublicDataAPI.get_instruments(instType="SWAP")
    data = get_valid_data(result)
    return data


# get_basic_info()

# def get_data():
#     result_list = get_market_data()["data"]
#     for i in result_list:
#         if i["instId"] == "BTC-USDT-SWAP":
#             print(str(i))

# while(1):
#     time.sleep(1)
#     print(get_current_price())

# k_line_history = get_k_line("1m")
# print(time.ctime(get_current_system_time(ms=0, int_value=1)))
# for i, one_k_line_record in enumerate(k_line_history):
#     print(i, time.ctime(change_time_type(one_k_line_record[0], ms=0, int_value=1)), end=" ")
#     print(one_k_line_record)

def get_position():
    result = accountAPI.get_positions()
    return result


if __name__ == "__main__":
    # print(time.ctime(get_current_system_time(ms=0, int_value=1)))

    # for i in get_unfinish_order():
    #     print(i)

    # try:
    #     while(1):
    #         print(maintain_price_list())
    # except:
    #     print(111)


    # num = 0
    # for i in get_basic_info():
    #     if "-USDT-SWAP" in i["instId"]:
    #         num += 1
    #         print(i["instId"])

    # newest_30_price = maintain_price_list()
    # print(newest_30_price)
    # tmp = newest_30_price[-5:]
    # print(tmp)
    # ma5 = sum(newest_30_price[-5:])/5
    # print(ma5)

    pass