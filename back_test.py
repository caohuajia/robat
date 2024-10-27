
from test_coin_class import *


def get_change_list(coin):
    change_list = []
    with open("./data/15m/31days/"+coin+"_price.json", "r") as f:
        k_line_history = json.load(f)
        k_line_history.reverse() ##[old ... new]
        price_history = []
        for i in k_line_history:
            price_history.append(float(i[1]))

        remain_price_history = price_history[96:]
        remain_num = len(remain_price_history)
        offset = 96

        for i in range(remain_num):
            idx = i + offset
            cur_price = price_history[idx]
            one_day_before_piece = price_history[idx-4*24:idx-4*24+2]
            one_day_before_average = sum(one_day_before_piece)/len(one_day_before_piece)
            change = cur_price/one_day_before_average - 1
            change_list.append(change)
    return change_list

if __name__ == "__main__":

    total_days = 1 + 30
    interval = "15m"
    test_one = 1
    test_coin = "CETUS"
    download_data = 0


    price_json_file = "_price_list.json"
    k_line_history = []
    all_coins = get_all_swap_list()
    if download_data: ## save_history_to_file
        coin_num = len(all_coins)
        for c in range(coin_num):
            k_line_history = get_history_k_line(all_coins[c], interval, int(total_days * 24*60/100/15)) ##[new ... old]  2s/200min  15s/day  1day=1440min
            k_line_history.reverse()
            # print(len(k_line_history))
            for i in k_line_history:
                i[0] = time.ctime(change_time_type(i[0], ms=0, int_value=1))
            file_name = "./data/"+interval+"/"+str(total_days)+"days/"+all_coins[c] + "_price.json"
            # print(file_name)
            with open(file_name, "w") as f:
                dumps = json.dumps(k_line_history)
                f.write(dumps)
            print("finish {}/{}".format(c, coin_num))
            time.sleep(2)
        exit(0)

    all_result = ""
    total_gain = 0


    btc_change_list = get_change_list("BTC")
    eth_change_list = get_change_list("ETH")

    for one_coin in all_coins:
        if test_one:
            one_coin = test_coin
        with open("./data/"+interval+"/"+str(total_days)+"days/" + one_coin + "_price.json", "r") as f:
            k_line_history = json.load(f)
            if interval == "15m":
                coin = coin_15m(one_coin, k_line_history[0:96])
            else:
                coin = coin_1m(one_coin, k_line_history[0:96])
            remain_k_line_history_piece = k_line_history[96:]
            remain_num = len(remain_k_line_history_piece)
            offset = 96
            for i in range(remain_num):
                btc_change = btc_change_list[i]
                eth_change = btc_change_list[i]
                coin.run(remain_k_line_history_piece[i])
            coin.finish()
            all_result += "{:<10}:  total: {:.3f}  balance: {:.3f}  blow num: {}\n".format(one_coin, coin.float_money, coin.balance, coin.blow_up_num)
            # print(total_days,"days " + one_coin + " finish: total: ",coin.float_money, "balance: ", coin.balance)
            total_gain += coin.float_money - 1
        if test_one:
            break
    all_result += "total gain: {}".format(total_gain)
    print("total gain: ",total_gain)
    with open("./log/all_test_log", "w") as f:
        f.write(all_result)

