import numpy as np
import json
import os


## list2 == list1 * k + b
def relation(list1, list2):
    Xi = list1
    Yi = list2
    A = np.vstack([Xi, np.ones(len(Xi))]).T
    k, b = np.linalg.lstsq(A, Yi, rcond=None)[0]
    return k, b


def get_2_coin_list(coin1, coin2):
    coin1_list = []
    coin2_list = []
    with open(f"./data/15m/31days/{coin1}_price.json", "r") as f:
        k_line_history = json.load(f)
        k_line_history.reverse()  ##[old ... new]
        for i in k_line_history:
            coin1_list.append(float(i[4]))
    with open(f"./data/15m/31days/{coin2}_price.json", "r") as f:
        k_line_history = json.load(f)
        k_line_history.reverse()  ##[old ... new]
        for i in k_line_history:
            coin2_list.append(float(i[4]))
    if len(coin1_list) != len(coin2_list):
        print("Warning: length of two coin price list is different!")
    return np.array(coin1_list), np.array(coin2_list)


def get_variance(ls):
    newest = ls[-1]
    percent_list = []
    for i in ls:
        percent = i/newest
        percent_list.append(percent)
    return np.var(percent_list) * 100 / 2

def get_all_coin_name_from_file():
    for root, dirs, files in os.walk("./data/15m/31days/"):
        coin_list = []
        for file in files:
            if file.endswith("_price.json"):
                coin_name = file.replace("_price.json", "")
                if coin_name.islower(): ## remove self define data
                    continue
                coin_list.append(coin_name)
        return coin_list

def get_2_coin_variance(coin1, coin2):
    coin1_list, coin2_list = get_2_coin_list(coin1, coin2)

    if len(coin1_list) != len(coin2_list):
        return None
    k, b = relation(coin1_list, coin2_list)
    shift_coin2_list = coin1_list * k + b
    variance = get_variance(coin1_list - shift_coin2_list)
    # print("coin2 = coin1 * {} + {}".format(k, b))
    # print("Variance:", variance)
    return variance
if __name__ == "__main__":
    coin_list = get_all_coin_name_from_file()
    base_coin = "ETH"
    for coin in coin_list:
        variance = get_2_coin_variance(base_coin, coin)
        print("{} - {} variance: {}".format(base_coin, coin, variance))
    # print("All coins: {} ".format(len(coin_list)), coin_list)
    # exit()





