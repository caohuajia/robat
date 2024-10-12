from base_okx import *


class Coin():
    global cur_ctime
    global config_dict
    log = ""
    coin_name = ""

    def __init__(self, coin_name):
        self.coin_name = coin_name

        self.get_self_config()

        ##  timestap         begin      highest    lowest     end                                      complete
        ##['1728006240000', '0.15846', '0.15859', '0.15785', '0.15785', '4480', '44800', '7090.9912', '0']
        k_line_100_history = get_k_line(self.coin_name, "1m") ##[new ... old]

        self.newest_80_history_price = []
        for i in range(80): ## 可能偶尔返回不了100个历史
            if 0: ##k_line_100_history[i][-1] == "0":
                continue ## newest does not finish
            else:
                end_price = k_line_100_history[i][4]
                self.newest_80_history_price.append(float(end_price)) ##[new ... old]
        self.newest_80_history_price.reverse() ##[old ... new]

    burst   = 0.01
    money_u = 1
    lever   = 10
    benefit = 0.01
    def get_self_config(self):
        self.burst   = config_dict[self.coin_name]["burst"]
        self.money_u = config_dict[self.coin_name]["money_u"]
        self.lever   = config_dict[self.coin_name]["lever"]
        self.benefit = self.burst


    open_num = 0
    ma5_buy_long_price   = 0
    ma5_sell_short_price = 0
    ma5_buy_long_stop    = 0
    ma5_sell_short_stop  = 0
    def gen_current_parameter(self):
        self.get_self_config()

        (self.newest_80_history_price).pop(0)
        (self.newest_80_history_price).append(float(get_current_swap_price(self.coin_name)))
        self.open_num = int(self.money_u // self.newest_80_history_price[-1])
        ma5 = sum(self.newest_80_history_price[-5:])/5
        newest_10_history_price = self.newest_80_history_price[-10:]
        threshold = get_variance(newest_10_history_price)
        self.ma5_buy_long_price   = ma5 * (1 - (self.burst + threshold))
        self.ma5_sell_short_price = ma5 * (1 + (self.burst + threshold))
        self.ma5_buy_long_stop    = self.ma5_buy_long_price  * (1+(self.burst + 2 * threshold))
        self.ma5_sell_short_stop  = self.ma5_sell_short_price * (1-(self.burst + 2 * threshold))

        self.log += self.coin_name + " ma5: " + str(ma5) + " burst: " + str(self.burst) + " thold: " + "{:.5f}".format(threshold*100) + "% newest_10: " + str(newest_10_history_price) + "\n"

    def create_order(self, side, posSide, price, tp_px):
        result = tradeAPI.place_order(
            tdMode="cross", ## cross:全仓杠杆/永续 isolated:逐仓杠杆/永续 cash:非保证金币币
            ccy   ="USDT",
            side  =side,   ## 开多：bug long   开空：sell short   平多：sell long   平空：bug short
            posSide=posSide, 
            ordType="limit", ## 限价：limit 市价：market
            sz     =str(self.open_num), ## 委托数量
            px     =price,   ## 委托价格 
            # attachAlgoOrds=1,
            tpTriggerPx=tp_px, ## 止盈价格
            tpOrdPx    =tp_px,
            # tpOrdKind  ="limit",
            clOrdId="",  ## 自定义订单id
            instId =self.coin_name+"-USDT-SWAP"
        )
        if result["code"] == "0":
            data = result["data"][0]
            order_id = data["ordId"]
            self.log += "["+cur_ctime + "] " + self.coin_name + " id:" + order_id + " " + side + " " + posSide + " create_success: " + \
                "price : " + str(price) + " ->| " + str(tp_px) + "\n"
            return order_id
        else:
            self.log += "["+cur_ctime + "] " + "create_order_fail: " + str(result) + " open_price: " + str(price) + " num: " + str(self.open_num) + "\n"
            return ""

    def modify_order(self, order_id, price, tp_px):
        result = tradeAPI.amend_order(
            newPx  =price,   ## 委托价格 
            ordId  =order_id,  
            # attachAlgoOrds=1,
            newTpTriggerPx=tp_px,
            newTpOrdPx    =tp_px,
            # newTpOrdOx    ="limit",
            instId =self.coin_name+"-USDT-SWAP"
        )
        if result["code"] == "0":
            data = result["data"][0]
            order_id = data["ordId"]
            self.log += "["+cur_ctime + "] " + self.coin_name + " id:" + order_id + " " + " modify_success: " + \
                "price : " + price + " ->| " + tp_px + "\n"
            return order_id
        else: ## modify fail, cancel order
            self.cancel_order(order_id)
            self.log += cur_ctime + " " + "modify_order_fail: " + str(result) + "\n"
            print(result)
            return ""

    def cancel_order(self, order_id):
        result = tradeAPI.cancel_order(
            ordId  =order_id,  
            instId =self.coin_name+"-USDT-SWAP"
        )
        if result["code"] == "0":
            data = result["data"][0]
            cl_ord_id = data["clOrdId"]
            print(cur_ctime, self.coin_name + " cancel order : " + "orderid: " + order_id )
        else:
            print("cancen fail: ", result)

    unfinish_order_num = 0
    def order_maintain(self, side, posSide, open_price, tp_px, old_order_id):
        global unfinish_order_list
        unfinish_id = []
        for i in unfinish_order_list:
            if (coin+"-USDT-SWAP") == i["instId"]:
                unfinish_id.append(i["ordId"])


        open_price = "{:.9f}".format(open_price)
        tp_px      = "{:.9f}".format(tp_px)

        ## modify
        if old_order_id != "":
            if old_order_id in unfinish_id:  ## modify
                modify_order_id = self.modify_order(old_order_id, open_price, tp_px)
                return modify_order_id
            else:  ## unknown, modify fail, means deal. So does not return, buy a new one
                self.log +=  "["+cur_ctime + "] id:" + old_order_id + " modify fail, unfinish: " + str(unfinish_id) + "\n"

        ## buy
        if self.unfinish_order_num <= 6:
            open_order_id = self.create_order(side, posSide, open_price, tp_px)
        else:
            self.log += self.coin_name + " order num > 6, not create order\n" 
        return open_order_id

    ma5_buy_long_id  = ""
    ma5_sell_short_id = ""
    def run(self):
        self.gen_current_parameter()
        self.ma5_buy_long_id   = self.order_maintain("buy", "long",   self.ma5_buy_long_price,   self.ma5_buy_long_stop,   self.ma5_buy_long_id )
        self.ma5_sell_short_id = self.order_maintain("sell", "short", self.ma5_sell_short_price, self.ma5_sell_short_stop, self.ma5_sell_short_id)
        log_info(self.log)
        self.log = ""
        pass


    def cancel_open_order(self):
        self.cancel_order(self.ma5_buy_long_id)
        self.cancel_order(self.ma5_sell_short_id)


if __name__ == "__main__":
    cur_ctime = time.ctime(get_current_system_time(ms=0, int_value=1))
    config_dict = get_config()
    coin_list = config_dict.keys()

    coin_obejcts = {}
    for coin_name in coin_list: ## TODO add/rm coin
        coin_obejcts[coin_name] = Coin(coin_name)

    time_flag_per_minite(cur_ctime)

    while 1:
        try:
            unfinish_order_list = get_unfinish_order()
            cur_ctime = time.ctime(get_current_system_time(ms=0, int_value=1))

            for coin in coin_obejcts.keys():
                coin_obejcts[coin].run()

            config_dict = get_config()
            coin_list = config_dict.keys()

            time_flag_per_minite(cur_ctime)
        except:
            for coin in coin_obejcts.keys():
                coin_obejcts[coin].cancel_open_order()
            break
    exit(0)

