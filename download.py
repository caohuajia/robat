from main import * 

def get_change_list(coin):
    change_list = []
    with open("./data/15m/31days/{}_price.json".format(coin), "r") as f:
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

def download(all_coins, interval, total_days):
    coin_num = len(all_coins)
    if interval == "15m":
        total_price_num = int(total_days * 24*60/100/15)  ## 15m
    elif interval == "1m":
        total_price_num = int(total_days * 24*60/100/1)  ## 1m  
    else:
        print("not support interval")
        exit(0)
    print("download {} {} days  {} price points each".format(interval, total_days, total_price_num))
    for c in range(coin_num):
        k_line_history = get_history_k_line(all_coins[c], interval, total_price_num) ##[new ... old]  2s/200min  15s/day  1day=1440min
        k_line_history.reverse()
        # print(len(k_line_history))
        for i in k_line_history:
            i[0] = time.ctime(change_time_type(i[0], ms=0, int_value=1))
        file_name = "./data/{}/{}days/{}_price.json".format(interval, str(total_days), all_coins[c])
        # print(file_name)
        with open(file_name, "w") as f:
            dumps = json.dumps(k_line_history)
            f.write(dumps)
        print("finish {}/{}  {}".format(c+1, coin_num, all_coins[c]))
        time.sleep(2)


if __name__ == "__main__":

    total_days = 1 + 30
    initial_money = 25
    interval = "15m"
    interval = "1m"
    all_coins = get_all_swap_list()
    download(all_coins, interval, total_days)
