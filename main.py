from base_okx import *


class Coin():
    global cur_ctime
    global config_dict
    log = ""
    coin_name = ""

    def __init__(self, coin_name):
        self.coin_name = coin_name
        self.unfinish_order_num = 0

        self.get_self_config()
        set_leverage(self.coin_name,self.lever)


        ##  timestap         begin      highest    lowest     end                                      complete
        ##['1728006240000', '0.15846', '0.15859', '0.15785', '0.15785', '4480', '44800', '7090.9912', '0']
        history_1m_k_line_100 = get_k_line(self.coin_name, "1m") ##[new ... old]

        self.newest_1m_100_history_price = []
        for i in range(98): ## 可能偶尔返回不了100个历史
            if 0: ##history_1m_k_line_100[i][-1] == "0":
                continue ## newest does not finish
            else:
                end_price_1m  = float(history_1m_k_line_100[i][4])
                self.newest_1m_100_history_price.append(end_price_1m) ##[new ... old]
        self.newest_1m_100_history_price.reverse() ##[old ... new]

    def update_newest_15m_100_history(self):

        ## ['1729861200000', '0.14621', '0.14662', '0.14578', '0.14656', '33498', '334980', '48981.5551', '1']
        history_15m_k_line_100 = get_k_line(self.coin_name, "15m") ##[new ... old]
        self.newest_15m_100_history_price = []
        for i in range(98): ## 可能偶尔返回不了100个历史
            if history_15m_k_line_100[i][-1]=="0": ##history_1m_k_line_100[i][-1] == "0":
                continue ## newest does not finish
            else:
                end_price_15m = float(history_15m_k_line_100[i][4])
                self.newest_15m_100_history_price.append(end_price_15m) ##[new ... old]
        self.newest_15m_100_history_price.reverse() ##[old ... new]

    def get_self_config(self):
        self.burst   = config_dict[self.coin_name]["burst"]
        self.gain    = config_dict[self.coin_name]["gain"]
        self.money_u = config_dict[self.coin_name]["money_u"]
        self.value   = config_dict[self.coin_name]["value"]
        self.lever   = config_dict[self.coin_name]["lever"]
        self.max_num = config_dict[self.coin_name]["max_num"]
        self.tdMode  = config_dict[self.coin_name]["tdMode"]

    def get_current_price(self):
        return float(get_current_swap_price(self.coin_name))

    def get_15m_ma60(self):
        self.update_newest_15m_100_history()

        n = -60
        newest_n =  self.newest_15m_100_history_price[n:]
        self.m_stable = sum(newest_n)/len(newest_n)

        refer_before = self.newest_15m_100_history_price[-4*24-1:-4*24+1]
        self.refer = sum(refer_before)/len(refer_before)

    def gen_current_parameter(self):
        self.get_self_config()

        # if self.flag_15m:
        self.get_15m_ma60()

        self.open_num = int(self.money_u * self.lever // (self.m_stable * self.value))
        self.buy_long_water_line   = self.refer * (1-(self.burst))
        self.sell_short_water_line = self.refer * (1+(self.burst))

        self.log += "[{}] ".format(cur_ctime) + self.coin_name + " ma60: {:.5f}".format(self.m_stable) + " refer: {:.5f}".format(self.refer) + " burst: " + str(self.burst) + \
                    " open_num: {:.5f}".format(self.open_num) + \
                    " buy long water line: {:.5f}".format(self.buy_long_water_line) + \
                    " sell short water line: {:.5f}".format(self.sell_short_water_line) + \
                    " newest_10: " + str(self.newest_15m_100_history_price[-10:]) + "\n"

    def create_order(self, side, posSide, price, num):
        result = tradeAPI.place_algo_order(
            tdMode=self.tdMode, ## cross:全仓杠杆/永续 isolated:逐仓杠杆/永续 cash:非保证金币币
            ccy   ="USDT",
            side  =side,   ## 开多：bug long   开空：sell short   平多：sell long   平空：bug short
            posSide=posSide, 
            ordType="trigger", ## 限价：limit 市价：market
            sz     = str(num), ## 委托数量

            triggerPx = price, ## 触发价格 
            orderPx   = price, ## 委托价格 
            instId =self.coin_name+"-USDT-SWAP"
        )

        if result["code"] == "0":
            data = result["data"][0]
            order_id = data["algoId"]
            self.log += "["+cur_ctime + "] " + self.coin_name + " id:" + order_id + " " + side + " " + posSide + " create_success: " + \
                "price : " + str(price) + "\n"
            return order_id
        else:
            self.log += "["+cur_ctime + "] " + "create_order_fail: " + str(result) + " open_price: " + str(price) + " num: " + str(num) + "\n"
            return ""

    def modify_order(self, order_id, price):
        # result = tradeAPI.amend_algo_order(
        #     newTriggerPx =price,   ## 触发价格 
        #     newOrdPx     =price,   ## 委托价格 
        #     algoId       =order_id,  
        #     instId       =self.coin_name+"-USDT-SWAP"
        # )
        # if result["code"] == "0":
        #     data = result["data"][0]
        #     order_id = data["algoId"]
        #     self.log += "["+cur_ctime + "] " + self.coin_name + " id:" + order_id + " " + " modify_success: " + \
        #         "price : " + price + "\n"
        #     return order_id
        # else: ## modify fail, cancel order
        #     self.cancel_order(order_id)
        #     self.log += cur_ctime + " " + "modify_order_fail: " + str(result) + "\n"
        #     print(result)
        #     return ""

        if self.cancel_order(order_id):
            pass
        else: ## cancel fail, maybe buy it
            self.unfinish_order_num += 1
        return ""


    def cancel_order(self, order_id):
        result = tradeAPI.cancel_algo_order(
            params= [{ "algoId":order_id, "instId" : self.coin_name+"-USDT-SWAP"}]
        )
        if result["code"] == "0":
            # data = result["data"][0]
            # cl_ord_id = data["clOrdId"]
            self.log += cur_ctime + " " +  self.coin_name + " cancel order : " + "orderid: " + order_id + "\n"
            return 1
        else:
            self.log += cur_ctime + " " +  self.coin_name + " cancel fail: " + "orderid: " + str(result) + "\n"
            return 0

    def order_maintain(self, side, posSide, open_price, old_order_id, num, position_value):
        # global unfinish_order_list
        global fill_order_list
        fill_id = []
        for i in fill_order_list:
            if (coin+"-USDT-SWAP") == i["instId"]:
                fill_id.append(i["ordId"])

        # self.unfinish_order_num = len(unfinish_id)
        
        open_price = "{:.9f}".format(open_price)

        ## modify
        if old_order_id != "":
            if old_order_id in fill_id:  ## fill, should not modify
                pass
            else:
                modify_order_id = self.modify_order(old_order_id, open_price)
                if modify_order_id == "": ## modify fail
                    pass
                else:
                    return modify_order_id
                # else:  ## unknown, modify fail, means deal. So does not return, buy a new one
                #     self.log +=  "["+cur_ctime + "] id:" + old_order_id + " modify fail, unfinish: " + str(unfinish_id) + "\n"

        ## buy
        if position_value < float(self.money_u):
            open_order_id = self.create_order(side, posSide, open_price, num)
            return open_order_id
        else:
            self.log += self.coin_name + " too more order, not create order\n" 
            return old_order_id

    buy_long_id  = ""
    sell_short_id = ""
    sell_long_id  = ""
    buy_short_id = ""
    def run(self, flag_15m = 0): ## 0:1m  1:15m
        self.flag_15m = flag_15m
        self.gen_current_parameter()

        self.long_position_value = 0
        self.short_position_value = 0

        global position_list
        buy_long_position = []
        sell_short_position = []
        for i in position_list:
            if (coin+"-USDT-SWAP") == i["instId"]:
                if i["posSide"] == "short":
                    sell_short_position.append({"price":float(i["avgPx"]), "number":i["pos"]})
                    self.short_position_value += (float(i["avgPx"]) * float(i["pos"]) * self.value / self.lever)
                if i["posSide"] == "long":
                    buy_long_position.append({"price":float(i["avgPx"]), "number":i["pos"]})
                    self.long_position_value += (float(i["avgPx"]) * float(i["pos"]) * self.value / self.lever)
        self.log += " long pos value:{} short pos value:{}\n".format(self.long_position_value, self.short_position_value)

        if len(buy_long_position):
            for i in buy_long_position:
                price = i["price"]
                num   = i["number"]
                if self.m_stable/price >= (1+float(self.gain)):
                    self.log += "try sell long {} {} \n".format(price, number)
                    self.sell_long_id = self.order_maintain("sell", "long", self.m_stable, self.sell_long_id, num, 0)
                else:
                    self.log += "fail sell long {} {}, target {:5f} \n".format(price, num, price*(1+float(self.gain)))
        
        if len(sell_short_position):
            for i in sell_short_position:
                price = i["price"]
                num   = i["number"]
                if self.m_stable/price <= (1-float(self.gain)):
                    # print("try buy short {} {}".format(price, number))
                    self.log += "try buy short {} {} \n".format(price, number)
                    self.buy_short_id = self.order_maintain("buy", "short", self.m_stable, self.buy_short_id, num, 0)
                else:
                    self.log += "fail buy short {} {}, target {:5f} \n".format(price, num, price*(1-float(self.gain)))
                    # print("fail buy short {} {}, target {}".format(price, num, price*(1-float(self.gain))))



        if self.m_stable <= self.buy_long_water_line:
            self.buy_long_id   = self.order_maintain("buy", "long",   self.m_stable, self.buy_long_id, self.open_num, self.long_position_value)
        else:
            self.log += " ma60 does not catch buy long water line   {:3f}%\n".format((self.m_stable / self.buy_long_water_line -1)*100)

        if self.m_stable >= self.sell_short_water_line or 1:
            self.sell_short_id = self.order_maintain("sell", "short", self.m_stable, self.sell_short_id, self.open_num, self.short_position_value)
        else:
            self.log += " ma60 does not catch sell short water line {:3f}%\n".format((self.sell_short_water_line / self.m_stable -1)*100)

        log_info(self.log)
        self.log = ""
        pass


    def cancel_open_order(self):
        self.cancel_order(self.buy_long_id)
        self.cancel_order(self.sell_short_id)


if __name__ == "__main__":
    cur_ctime = time.ctime(get_current_system_time(ms=0, int_value=1))
    config_dict = get_config()
    coin_list = config_dict.keys()

    coin_obejcts = {}
    for coin_name in coin_list: ## TODO add/rm coin
        coin_obejcts[coin_name] = Coin(coin_name)

    while 1:
        # try:
            config_dict = get_config()

            # unfinish_order_list = get_unfinish_order()
            fill_order_list = get_fills()
            position_list   = get_current_positions()
            cur_ctime = time.ctime(get_current_system_time(ms=0, int_value=1))

            for coin in coin_obejcts.keys():
                coin_obejcts[coin].run()

            print("sleep")
            time_flag_per_minite(cur_ctime)

        # except:
        #     print("kill and cancel order")
        #     for coin in coin_obejcts.keys():
        #         log_info(coin_obejcts[coin].log)
        #         coin_obejcts[coin].cancel_open_order()
        #     log_info(cur_ctime + " some exception\n")
        #     break
    exit(0)

