
from main import *

class coin_test():
    global config_dict
    log = ""

    def __init__(self, coin_name, k_line_100_history):
        self.coin_name = coin_name
        self.get_self_config()

        self.prefer_mode = 0  ## >0, prefer bug long, <0 prefer sell short

        self.hold_list = []
        self.total_money = 1
        self.balance = 1
        self.current_market = []

        self.newest_80_history_price = []
        for i in range(1500): ## 可能偶尔返回不了100个历史
            begin_price = k_line_100_history[i][1]
            self.newest_80_history_price.append(float(begin_price)) ##[new ... old]
        self.newest_80_history_price.reverse() ##[old ... new]


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

    def blow_up(self):
        self.get_float_money()
        # self.log += self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() + "\n"
        if self.float_money < 0.01:
            self.log += self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() + "\n"
            print(self.cur_ctime,"blow_up float_u:",self.float_money, "cur_price",self.cur_price)
            self.log_info(self.log, 1)
            exit(0)
        else:
            pass

    def buy_long(self):
        if self.balance>0.1:
            if self.buy_long_price > self.market_lowest:
                trade_info = {"time":self.cur_ctime, "price":self.buy_long_price, "money":0.01, "stop_price":self.buy_long_stop, "mode":0}
                self.balance -= 0.1
                self.hold_list.append(trade_info)
                self.log += "[buy ] " + self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() +\
                                             " bug long: " +  "{:.5f}".format(self.buy_long_price) + "->|" "{:.5f}".format(self.buy_long_stop) + "\n"

    def sell_short(self):
        if self.balance>0.1:
            if self.sell_short_price < self.market_highest:
                trade_info = {"time":self.cur_ctime, "price":self.sell_short_price, "money":0.01, "stop_price":self.sell_short_stop, "mode":1}
                self.balance -=0.1
                self.hold_list.append(trade_info)
                self.log += "[sell] " + self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() +\
                                             " sell short: " +  "{:.5f}".format(self.sell_short_price) + "->|" "{:.5f}".format(self.sell_short_stop) + "\n"


    def deal(self):
        for i in self.hold_list:
            can_deal = 0
            if i["mode"]: ## sell, stop need buy
                if i["stop_price"] > self.market_lowest:
                    can_deal = 1
            else: ## buy, stop need sell
                if i["stop_price"] < self.market_highest:
                    can_deal = 1

            if can_deal:
                self.log += "[deal] " + self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() + \
                                             " deal: " + "{:.5f}".format(i["stop_price"]) + "\n"
                self.total_money += 0.1 * self.gain * self.lever 
                self.balance     += 0.1 + 0.1 * self.gain * self.lever 
                self.hold_list.remove(i)
            else:
                pass


    def get_current_price(self):
        return float(self.cur_price)

    def gen_current_parameter(self):
        self.get_self_config()

        (self.newest_80_history_price).pop(0)
        (self.newest_80_history_price).append(self.get_current_price())

        newest_5 = self.newest_80_history_price[-5:]
        ma5 = sum(newest_5)/len(newest_5)
        newest_10_history_price = self.newest_80_history_price[-8:]
        threshold = get_variance(newest_10_history_price)
        self.buy_long_price   = ma5 * (1 - (self.burst + 1 * threshold))
        self.sell_short_price = ma5 * (1 + (self.burst + 1 * threshold))
        self.buy_long_stop    = self.buy_long_price   * (1+self.gain)
        self.sell_short_stop  = self.sell_short_price * (1-self.gain)

        # self.log += self.coin_name + " ma5: " + str(ma5) + " burst: " + str(self.burst) + " thold: " + "{:.5f}".format(threshold*100) + "% newest_10: " + str(newest_10_history_price) + "\n"

        # self.one_day_before_average = sum(self.newest_80_history_price[-1499:-1380])/len(self.newest_80_history_price[-1499:-1380])
        # self.buy_long_price   = self.one_day_before_average * (1-self.burst - len(self.hold_list)*0.05)
        # self.sell_short_price = self.one_day_before_average * (1+self.burst - len(self.hold_list)*0.05)
        # self.buy_long_stop    = self.buy_long_price    * (1+self.gain)
        # self.sell_short_stop  = self.sell_short_price  * (1-self.gain)

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

            self.burst   = config_dict[self.coin_name]["burst"]
            self.gain    = config_dict[self.coin_name]["gain"]
            self.lever   = config_dict[self.coin_name]["lever"]
            self.stable_slope    = 0.001
            self.tdMode = 1 if config_dict[self.coin_name]["tdMode"] == "isolated" else 0

    def run(self, current_market):
        ## ["Sun Oct 13 20:26:00 2024", "0.21326", "0.21388", "0.21323", "0.21368", "6935", "69350", "14809.0594", "1"],
        self.market_piece = current_market
        self.market_highest = float(self.market_piece[2])
        self.market_lowest  = float(self.market_piece[3])

        self.cur_ctime = current_market[0]
        self.cur_price = float(current_market[1])
        self.gen_current_parameter()

        self.blow_up()
        self.deal()

        self.buy_long()
        self.sell_short()

        # if abs(polyfit(self.newest_80_history_price[-10:],1)[0]) < self.stable_slope:
            
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






if __name__ == "__main__":
    coin_name = "PEPE"
    price_json_file = "price_list.json"
    k_line_history = []
    total_days = 1 + 90
    if 0: ## save_history_to_file
        k_line_history = get_history_k_line(coin_name, "1m", int(total_days * 24*60/100)) ##[new ... old]  2s/200min  15s/day  1day=1440min
        k_line_history.reverse()
        print(len(k_line_history))
        for i in k_line_history:
            i[0] = time.ctime(change_time_type(i[0], ms=0, int_value=1))

        with open(price_json_file, "w") as f:
            dumps = json.dumps(k_line_history)
            f.write(dumps)
    else:
        with open(price_json_file, "r") as f:
            k_line_history = json.load(f)


    coin = coin_test(coin_name, k_line_history[0:1500])
    for market_piece in k_line_history[1501:]:
        coin.run(market_piece)
    coin.finish()
    print(total_days,"days finish: total: ",coin.float_money, "balance: ", coin.balance)
    # pass