
from main import *

class coin_test():
    global config_dict
    log = ""
    coin_name = ""

    def __init__(self, coin_name, k_line_100_history):
        self.coin_name = coin_name
        self.get_self_config()

        self.hold_list = []
        self.total_money = 1
        self.balance = 1
        self.current_market = []

        self.newest_80_history_price = []
        for i in range(80): ## 可能偶尔返回不了100个历史
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
        hold_str = " hold:"
        for i in self.hold_list:
            hold_str += "{:.5f}".format(i["price"]) + " "
        return hold_str


    float_money = 0
    def get_float_money(self):
        self.float_money = self.total_money
        for i in self.hold_list:
            if i["mode"] == 0: ## buy more
                self.float_money += 0.1 * (self.cur_price / float(i["price"]) - 1) * 10
            else:
                self.float_money += 0.1 * (1- self.cur_price / float(i["price"])) * 10

    def blow_up(self):
        self.get_float_money()
        # self.log += self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() + "\n"
        if self.float_money < 0.01:
            self.log += self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() + "\n"
            print(self.cur_ctime,"blow_up",self.total_money, self.cur_price)
            self.log_info(self.log, 1)
            exit(0)
        else:
            pass

    def buy_long(self):
        if self.balance>0.1:
            if self.price_can_trade(self.ma5_buy_long_price):
                trade_info = {"time":self.cur_ctime, "price":self.ma5_buy_long_price, "money":0.01, "stop_price":self.ma5_buy_long_stop, "mode":0}
                self.balance -= 0.1
                self.hold_list.append(trade_info)
                self.log += self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() +\
                                             " bug long: " +  "{:.5f}".format(self.ma5_buy_long_price) + "->|" "{:.5f}".format(self.ma5_buy_long_stop) + "\n"

    def sell_short(self):
        if self.balance>0.1:
            if self.price_can_trade(self.ma5_sell_short_price):
                trade_info = {"time":self.cur_ctime, "price":self.ma5_sell_short_price, "money":0.01, "stop_price":self.ma5_sell_short_stop, "mode":1}
                self.balance -=0.1
                self.hold_list.append(trade_info)
                self.log += self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() +\
                                             " sell short: " +  "{:.5f}".format(self.ma5_sell_short_price) + "->|" "{:.5f}".format(self.ma5_sell_short_stop) + "\n"


    def deal(self):
        for i in self.hold_list:
            if self.price_can_trade(i["stop_price"]):
                self.total_money += 0.01 
                self.balance     += 0.11
                self.hold_list.remove(i)
                self.log += self.cur_ctime + " u/b:" + "{:.5f}".format(self.float_money) + "/" + "{:.5f}".format(self.balance) + " " + "{:.5f}".format(self.cur_price) + self.get_cur_hold() + \
                                             " deal: " + "{:.5f}".format(i["stop_price"]) + "\n"
            else:
                pass


    def get_current_price(self):
        return float(self.cur_price)

    def get_self_config(self):
        self.burst   = 0.01

    def gen_current_parameter(self):
        self.get_self_config()

        (self.newest_80_history_price).pop(0)
        (self.newest_80_history_price).append(self.get_current_price())
        ma5 = sum(self.newest_80_history_price[-5:])/5
        newest_10_history_price = self.newest_80_history_price[-10:]
        threshold = get_variance(newest_10_history_price)
        self.ma5_buy_long_price   = ma5 * (1 - (self.burst + threshold))
        self.ma5_sell_short_price = ma5 * (1 + (self.burst + threshold))
        self.ma5_buy_long_stop    = self.ma5_buy_long_price  * (1+(self.burst + 2 * threshold))
        self.ma5_sell_short_stop  = self.ma5_sell_short_price * (1-(self.burst + 2 * threshold))

        # self.log += self.coin_name + " ma5: " + str(ma5) + " burst: " + str(self.burst) + " thold: " + "{:.5f}".format(threshold*100) + "% newest_10: " + str(newest_10_history_price) + "\n"

    def price_can_trade(self, price):
        highest = float(self.market_piece[2])
        lowest  = float(self.market_piece[3])
        price   = float(price)
        if price > lowest:
            if price < highest:
                return 1
        return 0

    def run(self, current_market):
        ## ["Sun Oct 13 20:26:00 2024", "0.21326", "0.21388", "0.21323", "0.21368", "6935", "69350", "14809.0594", "1"],
        self.market_piece = current_market
        self.cur_ctime = current_market[0]
        self.cur_price = float(current_market[1])
        self.gen_current_parameter()

        self.blow_up()
        self.deal()

        self.buy_long()
        self.sell_short()

        self.log_info(self.log, 1)
        self.log = ""
        pass






if __name__ == "__main__":
    coin_name = "CETUS"
    price_json_file = "price_list.json"
    k_line_history = []
    if 0: ## save_history_to_file
        k_line_history = get_history_k_line(coin_name, "1m", int(4 * 24*60/100)) ##[new ... old]  2s/200min  15s/day
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


    coin = coin_test(coin_name, k_line_history[0:80])
    for market_piece in k_line_history[81:]:
        coin.run(market_piece)
    print("finish: total: ",coin.total_money, "balance: ", coin.balance)
    # pass