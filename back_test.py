
from main import *

class coin_test():
    global config_dict
    log = ""

    def __init__(self, coin_name, k_line_100_history):
        self.coin_name = coin_name
        self.get_self_config()

        self.prefer_mode = 0  ## >0, prefer bug long, <0 prefer sell short
        self.blow_up_num = 0

        self.hold_list = []
        self.total_money = 1
        self.balance = 1
        self.current_market = []

        self.newest_history_price = []
        for i in range(len(k_line_100_history)): ## 可能偶尔返回不了100个历史
            begin_price = k_line_100_history[i][1]
            self.newest_history_price.append(float(begin_price)) ##[new ... old]
        self.newest_history_price.reverse() ##[old ... new]
        # self.newest_80_history_price = self.newest_history_price[-80:]


        with open("test.log", "w") as f:
            f.write("")
        pass

    def log_info(self, log, keep_cur_line=0):
        with open("test.log", "a+") as f:
            f.write(log)
            if keep_cur_line:
                pass
            else:
                f.write("\n")

    def prob(self):
        if "Sep 30 05" in self.cur_ctime and 0:
            self.log += "[prob] " + self.cur_ctime + " cur_price: {:.5f}".format(self.cur_price) + " bef_24h: {:.5f}".format(self.one_day_before_average) + \
                                " rise: {:.0f}%".format(self.cur_price/self.one_day_before_average*100) + " sell short: {:.5f}".format(self.sell_short_price) + \
                                " need: {:.1f}%".format((self.sell_short_price/self.cur_price-1)*100) + " ma60 {:.5f}".format(self.ma60) + "\n"

    def get_cur_hold(self):
        hold_str = " p_m: " + "{:.1f}".format(self.prefer_mode) + " hold:{"
        for i in self.hold_list:
            if i["mode"] == 0: ## buy more
                hold_str += "{:.5f}".format(i["price"]) + " " + "{:.0f}".format((self.cur_price/i["price"]-1)*100*self.lever) + "% "
            else:
                hold_str += "{:.5f}".format(i["price"]) + " " + "{:.0f}".format((1-self.cur_price/i["price"])*100*self.lever) + "% "
        hold_str += "}"
        return hold_str

    def finish(self):
        self.get_float_money()
        self.log += "[finl] " + self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() + "\n"
        self.log_info(self.log, 1)

    float_money = 0
    def get_float_money(self):
        self.float_money = self.total_money
        for i in self.hold_list:
            if i["mode"] == 0: ## buy more
                benefit_rate = (self.cur_price / float(i["price"]) - 1) * self.lever
                self.float_money += 0.1 * benefit_rate
                self.prefer_mode += benefit_rate
                if self.tdMode:
                    if benefit_rate < -1:
                        self.log += "[blow] " + self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + \
                                        "{:.5f}".format(self.cur_price) + self.get_cur_hold() + " order blow up\n"
                        self.hold_list.remove(i)
                        self.total_money -= 0.1
                        self.blow_up_num += 1
            else:
                benefit_rate = (1- self.cur_price / float(i["price"])) * self.lever
                self.float_money += 0.1 * benefit_rate
                self.prefer_mode -= benefit_rate
                if self.tdMode:
                    if benefit_rate < -1:
                        self.log += "[blow] " + self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + \
                                        "{:.5f}".format(self.cur_price) + self.get_cur_hold() + " order blow up\n"
                        self.hold_list.remove(i)
                        self.total_money -= 0.1
                        self.blow_up_num += 1

    def blow_up(self):
        # cur_slope = abs(polyfit(self.newest_80_history_price,1)[0])
        # variance  = get_variance(self.newest_80_history_price)
        # self.log += self.cur_ctime + " slope: " + "{:.7f}".format(cur_slope*100000) + " variance " + "{:.5f}".format(variance) + "\n"

        self.get_float_money()
        # self.log += self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() + "\n"
        if self.float_money < 0.01:
            self.log += self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() + "\n"
            print(self.cur_ctime,"blow_up float_u:",self.float_money, "cur_price",self.cur_price)
            self.log_info(self.log, 1)
            exit(0) ##TODO
        else:
            pass

    def buy_long(self):
        self.prob()
        if self.balance>0.1:
            if self.buy_long_price > self.market_lowest:
                if self.price_can_trade(self.ma60):
                    trade_info = {"time":self.cur_ctime, "price":self.cur_price, "money":0.01, "stop_price":self.buy_long_stop, "mode":0}
                    self.balance -= 0.1
                    self.hold_list.append(trade_info)
                    self.log += "[buy ] " + self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() +\
                                                " bug long: " +  "{:.5f}".format(self.buy_long_price) + "->|" "{:.5f}".format(self.buy_long_stop) + "\n"
                    self.log += " one_day before: {:.5f}".format(self.one_day_before_average) + " {:.5f}".format(self.cur_price/self.one_day_before_average) +\
                                " ma60: {:.5f}".format(self.ma60) + " {:.5f}".format(self.ma60/self.cur_price) +\
                                " cur_high: {:.5f}".format(self.market_highest) + " cur_low: {:.5f}".format(self.market_lowest) + \
                                " burst: {:.5f}".format((1+(self.burst + self.ma60_gap + self.sell_short_num * 0.15))) + \
                                " btc/eth: {:.5f}".format( btc_change + eth_change) + \
                                "\n"

    def sell_short(self):
        self.prob()
        if self.balance>0.1:
            if self.sell_short_price < self.market_highest:
                if self.price_can_trade(self.ma60):
                    trade_info = {"time":self.cur_ctime, "price":self.cur_price, "money":0.01, "stop_price":self.sell_short_stop, "mode":1}
                    self.balance -=0.1
                    self.hold_list.append(trade_info)
                    self.log += "[sell] " + self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() +\
                                                " sell short: " +  "{:.5f}".format(self.sell_short_price) + "->|" "{:.5f}".format(self.sell_short_stop) + "\n"
                    self.log += " one_day before: {:.5f}".format(self.one_day_before_average) + " {:.5f}".format(self.cur_price/self.one_day_before_average) +\
                                " ma60: {:.5f}".format(self.ma60) + " {:.5f}".format(self.ma60/self.cur_price) +\
                                " cur_high: {:.5f}".format(self.market_highest) + " cur_low: {:.5f}".format(self.market_lowest) + \
                                " burst: {:.5f}".format((1+(self.burst + self.ma60_gap + self.sell_short_num * 0.15))) + \
                                " btc/eth: {:.5f}".format( btc_change + eth_change) + \
                                "\n"


    def deal(self):
        self.buy_long_num   = 0
        self.sell_short_num = 0
        for i in self.hold_list:
            can_deal = 0
            if i["mode"]: ## sell, stop need buy
                if self.price_can_trade(self.ma60):
                    delivery_benefit = 1-self.market_lowest/i["price"]
                    if delivery_benefit > self.gain:
                        can_deal = 1
                    else:
                        self.sell_short_num += 1
                else:
                    self.sell_short_num += 1

            else: ## buy, stop need sell
                if self.price_can_trade(self.ma60):
                    delivery_benefit = self.market_highest/i["price"]-1
                    if delivery_benefit > self.gain:
                        can_deal = 1
                    else:
                        self.buy_long_num += 1
                else:
                    self.sell_short_num += 1

            if can_deal:
                if self.price_can_trade(self.ma60):
                    self.log += "[deal] " + self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() + \
                                                " deal: " + "{:.5f}".format(i["stop_price"]) + "\n"
                    self.total_money += 0.1 * delivery_benefit * self.lever 
                    self.balance     += 0.1 + 0.1 * delivery_benefit * self.lever 
                    self.hold_list.remove(i)
            else:
                pass

    def gen_current_parameter(self):
        (self.newest_history_price).pop(0)
        (self.newest_history_price).append(self.cur_price)

        newest_60 =  self.newest_history_price[-60:]
        self.ma60 = sum(newest_60)/len(newest_60)
        one_day_before_piece = self.newest_history_price[-4*24-1:-4*24+1]
        self.one_day_before_average = sum(one_day_before_piece)/len(one_day_before_piece)

        # self.ma60_gap = min(5*abs(self.cur_price/self.ma60-1) , 0.2)
        self.ma60_gap = 0

        # global btc_change
        # global eth_change
        btc_change = 0
        eth_change = 0

        self.buy_long_price   = self.one_day_before_average * (1-(self.burst + self.ma60_gap + self.buy_long_num   * 0.15 + btc_change + eth_change))
        self.sell_short_price = self.one_day_before_average * (1+(self.burst + self.ma60_gap + self.sell_short_num * 0.15 + btc_change + eth_change))
        self.buy_long_stop    = self.buy_long_price    * (1+self.gain)
        self.sell_short_stop  = self.sell_short_price  * (1-self.gain)

    def price_can_trade(self, price):
        highest = float(self.market_piece[2])
        lowest  = float(self.market_piece[3])
        price   = float(price)
        if price > lowest:
            if price < highest:
                return 1
        return 0

    def get_self_config(self):
        with open("test_config.json", "r") as f:
            config_dict = json.load(f)[0]

            # self.burst   = config_dict[self.coin_name]["burst"]
            # self.gain    = config_dict[self.coin_name]["gain"]
            # self.lever   = config_dict[self.coin_name]["lever"]
            # self.stable_slope    = 0.001
            # self.tdMode = 1 if config_dict[self.coin_name]["tdMode"] == "isolated" else 0

            self.burst   = config_dict["CETUS"]["burst"]
            self.gain    = config_dict["CETUS"]["gain"]
            self.lever   = config_dict["CETUS"]["lever"]
            self.stable_slope    = 0.001
            self.tdMode = 1 if config_dict["CETUS"]["tdMode"] == "isolated" else 0

    def run(self, current_market):
        ## ["Sun Oct 13 20:26:00 2024", "0.21326", "0.21388", "0.21323", "0.21368", "6935", "69350", "14809.0594", "1"],
        self.market_piece = current_market
        self.market_highest = float(self.market_piece[2])
        self.market_lowest  = float(self.market_piece[3])

        self.cur_ctime = current_market[0]
        self.cur_price = float(current_market[1])

        self.blow_up()
        self.deal()

        self.gen_current_parameter()

        if self.buy_long_num <= 2:
            self.buy_long()
        if self.sell_short_num <=2:
            self.sell_short()

        # if abs(polyfit(self.newest_history_price[-10:],1)[0]) < self.stable_slope:
            
        #     if self.prefer_mode > -1.0:
        #         if len(self.hold_list)<=3:
        #             self.buy_long()
        #     if self.prefer_mode < 1.0:
        #         if len(self.hold_list)<=3:
        #             self.sell_short()

        self.log_info(self.log, 1)
        self.log = ""
        self.prefer_mode = 0
        pass


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
    price_json_file = "_price_list.json"
    k_line_history = []
    total_days = 1 + 30
    interval = "15m"
    all_coins = get_all_swap_list()
    if 0: ## save_history_to_file
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

    test_one = 1

    for one_coin in all_coins:
        if test_one:
            one_coin = "CETUS"
        with open("./data/15m/31days/" + one_coin + "_price.json", "r") as f:
            k_line_history = json.load(f)

            coin = coin_test(one_coin, k_line_history[0:96])
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
    with open("all_test_log", "w") as f:
        f.write(all_result)

