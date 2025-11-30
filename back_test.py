# coding=UTF-8

from test_coin_class import *


def get_all_coin_obj(all_coins):
    all_coin_struct = {}
    for one_coin in all_coins:
        if test_one:
            one_coin = test_coin
        # try:
        if 1:
            with open("./data/{}/{}days/{}_price.json".format(interval, str(total_days), one_coin), "r") as f:
                k_line_history = json.load(f)
                if interval == "15m":
                    coin = coin_15m(one_coin, k_line_history)
                    all_coin_struct[one_coin] = coin

                else:
                    offset = 1440  ## 1440min = 24h
                    coin = coin_1m(one_coin, k_line_history[0:offset])
                    remain_k_line_history_piece = k_line_history[offset:]
                    remain_num = len(remain_k_line_history_piece)
                    for i in range(remain_num):
                        # btc_change = btc_change_list[i]
                        # eth_change = btc_change_list[i]
                        if coin.run(remain_k_line_history_piece[i]):
                            break
        # except:
        else:
            print("{} is not downloaded".format(one_coin))
        if test_one:
            break
    return all_coin_struct


if __name__ == "__main__":

    total_days = 1 + 30
    initial_money = 25
    interval = "15m"
    #interval = "1m"
    test_one = 1
    # test_coin = "11test"
    test_coin = "DOGE"
    test_coin = "OKB"

    # all_coins = get_all_swap_list()
    all_coins = ["DOGE", "ETH"]
    # btc_change_list = get_change_list("BTC")
    # eth_change_list = get_change_list("ETH")

    all_coin_struct = get_all_coin_obj(all_coins)

    all_result = ""
    total_gain = 0

    round = 0
    global_money = [initial_money]
    while 1:
        for one_coin in list(all_coin_struct.keys()):
            coin = all_coin_struct[one_coin]
            if coin.run(global_money):
                coin.finish()
                all_result += "{:<10}:  total: {:.3f}  balance: {:.3f}  blow num: {}\n".format(one_coin, coin.float_money, coin.balance, coin.blow_up_num)
                # print(total_days,"days " + one_coin + " finish: total: ",coin.float_money, "balance: ", coin.balance)
                total_gain += coin.float_money - 1
                all_coin_struct.pop(one_coin)
        if len(list(all_coin_struct.keys())) == 0:
            break
        else:
            round += 1
            # print("round {}/{}".format(round,1))

    all_result += "total gain: {}%".format(total_gain/initial_money*100)
    print("total gain: {}%".format(total_gain/initial_money*100))
    if test_one:
        pass
    else:
        with open("./log/all_test_log", "w") as f:
            f.write(all_result)

