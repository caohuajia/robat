# coding=UTF-8

from test_coin_class import *
from datetime import datetime

# 输出：Mon Oct  6 17:15:00 2025    ->  10/06 17:15
def simplify_time(time_str):
    dt = datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
    return dt.strftime("%m/%d %H:%M")

def get_all_coin_obj(all_coins):
    all_coin_struct = {}
    for one_coin in all_coins:
        if test_one:
            one_coin = test_coin
        # try:
        if 1:
            with open("./data/{}/{}days/{}_price.json".format(interval, str(total_days), one_coin), "r") as f:
                if interval == "15m":
                    coin = coin_base(one_coin, interval, total_days)
                    all_coin_struct[one_coin] = coin

                else:
                    coin = coin_1m(one_coin, interval, total_days)
                    all_coin_struct[one_coin] = coin
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

    if test_one:
        # for test_coin in ["OKB", "DOGE", "CETUS", "ETH", "BTC"]:
        for test_coin in ["BTC"]:
            # for burst in [0.01,0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]:
            for burst in [0.00]:
                # for gain in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]:
                for gain in [0.01]:
                    # for m_base in [30, 60]:
                    for m_base in [60]:
                        total_gain = 0
                        round = 0
                        global_money = [initial_money]
                        all_coin_struct = get_all_coin_obj(all_coins)
                        coin = all_coin_struct[test_coin]
                        coin.burst = burst
                        coin.gain = gain
                        coin.m_base = m_base
                        while 1:
                            run_can_done = coin.run(global_money)
                            if run_can_done: ## continue until finish
                                coin.finish()
                            all_result += "{:<10}:  float: {:.3f}  balance: {:.3f}  blow num: {}\n".format(test_coin, coin.float_money, coin.balance, coin.blow_up_num)
                            # print(total_days,"days " + one_coin + " finish: total: ",coin.float_money, "balance: ", coin.balance)
                            total_gain = (coin.float_money - 1)
                            if run_can_done:
                                break

                        all_result += "total gain: {}%".format((total_gain/1)*100)
                        print("total gain: {}%".format((total_gain/1)*100))
                        with open("./log/all_test_log", "w") as f:
                            f.write(all_result)

                        with open("./data/{}/{}days/{}_price.json".format(interval, str(total_days), test_coin), "r") as f:
                            k_line_history = json.load(f)
                            begin_price = float(k_line_history[0][1])
                            begin_time = k_line_history[0][0]
                            end_price = float(k_line_history[-1][1])
                            end_time = k_line_history[-1][0]
                        with open("./all_try_log.log", "a") as f:
                            # print(len(k_line_history))
                            f.write("{:<8} total_gain:{:>8}  m_base: {}  burst: {:.2f}  gain: {:.2f}  lever: {}  hit_m up/dn: {}-{}  time: {}  ~  {}  period_price: {:.2f}% \n".format(
                                    coin.coin_name, "{:.2f}%".format((total_gain/1)*100), coin.m_base, coin.burst, coin.gain, coin.lever, coin.hit_m_up, coin.hit_m_dn, simplify_time(begin_time), simplify_time(end_time), ((end_price/begin_price)-1)*100))




    else:
        while 1:
            for one_coin in list(all_coin_struct.keys()):
                coin = all_coin_struct[one_coin]
                if coin.run(global_money):
                    coin.finish()
                    all_result += "{:<10}:  float: {:.3f}  balance: {:.3f}  blow num: {}\n".format(one_coin, coin.float_money, coin.balance, coin.blow_up_num)
                    # print(total_days,"days " + one_coin + " finish: total: ",coin.float_money, "balance: ", coin.balance)
                    total_gain += (coin.float_money - 1)
                    all_coin_struct.pop(one_coin)
            if len(list(all_coin_struct.keys())) == 0:
                break
            else:
                round += 1
                # print("round {}/{}".format(round,1))

        if test_one:
            all_result += "total gain: {}%".format((total_gain/1)*100)
            print("total gain: {}%".format((total_gain/1)*100))
            with open("./log/all_test_log", "w") as f:
                f.write(all_result)

            with open("./data/{}/{}days/{}_price.json".format(interval, str(total_days), test_coin), "r") as f:
                k_line_history = json.load(f)
                begin_price = float(k_line_history[0][1])
                begin_time = k_line_history[0][0]
                end_price = float(k_line_history[-1][1])
                end_time = k_line_history[-1][0]
            with open("./all_try_log.log", "a") as f:
                # print(len(k_line_history))
                f.write("{:<8} total_gain:{:>8}  m_base: {}  burst: {:.2f}  gain: {:.2f}  lever: {}  hit_m up/dn: {}-{}  time: {}  ~  {}  period_price: {:.2f}% \n".format(
                        test_coin, "{:.2f}%".format((total_gain/1)*100), coin.m_base, coin.burst, coin.gain, coin.lever, coin.hit_m_up, coin.hit_m_dn, simplify_time(begin_time), simplify_time(end_time), ((end_price/begin_price)-1)*100))
            pass
        else:
            all_result += "total gain: {}%".format((total_gain/initial_money)*100)
            print("total gain: {}%".format((total_gain/initial_money)*100))
            with open("./log/all_test_log", "w") as f:
                f.write(all_result)

