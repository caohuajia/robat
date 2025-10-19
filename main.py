from base_okx import *

class Coin():
    global cur_ctime
    global config_dict
    global prefer_idx
    global back_test
    log = ""
    coin_name = ""

    def __init__(self, coin_name, time_mode="1m"):
        self.coin_name = coin_name
        self.init = 0
        self.time_mode = time_mode

        self.get_self_config()
        self.set_leverage()
        
        self.get_swap_value()
        self.newest_1m_history_price = []
        if self.time_mode == "1m":
            pass
            # self.update_newest_300_history()
        else:
            pass
            # self.update_newest_15m_300_history()
            # self.update_newest_1h_300_history()

    def set_leverage(self):
        global global_log
        result = set_long_leverage(self.coin_name+"-USDT-SWAP", self.b_lever, "isolated")
        if "'code': '0'" in result:
            pass
        else:
            self.log += "set leverage fail: " + result + "\n"
            global_log += "{} set leverage fail: ".format(self.coin_name) + result + "\n"

        result = set_short_leverage(self.coin_name+"-USDT-SWAP", self.s_lever, "isolated")
        if "'code': '0'" in result:
            pass
        else:
            self.log += "set leverage fail: " + result + "\n"
            global_log += "{} set leverage fail: ".format(self.coin_name) + result + "\n"

    def get_swap_value(self):
        global public_data
        for i in public_data:
            if (self.coin_name+"-USDT-SWAP") == i["instId"]:
                self.value = float(i["ctVal"])

    def price_hit(self, price_piece, price):
        highest = float(price_piece[2])
        lowest  = float(price_piece[3])
        if price > lowest:
            if price < highest:
                return 1
        return 0


    def update_newest_1h_300_history(self):
        history_1h_k_line_300 = get_k_line(self.coin_name, cur_int_time_ms, "1H") ##[new ... old] 300 result
        # print(history_1h_k_line_300)
        self.newest_1h_300_history_price = []
        try:
            for i in range(298): ## 可能偶尔返回不了100个历史
                if history_1h_k_line_300[i][-1]=="0": ##history_1m_k_line_100[i][-1] == "0":
                    continue ## newest does not finish
                else:
                    end_price_1h = float(history_1h_k_line_300[i][4])
                    self.newest_1h_300_history_price.append(end_price_1h) ##[new ... old]
            self.newest_1h_300_history_price.reverse() ##[old ... new]
        except:
            print("{} can not get 1h 300 history".format(self.coin_name))
            return

        refer_before = self.newest_1h_300_history_price[-4*24*3:]
        self.refer_1h_300 = sum(refer_before)/len(refer_before)


    def update_newest_300_history(self): ## does not use, 1m need push current price to get newest history
        ##  timestap         begin      highest    lowest     end                                      complete
        ## ['1729861200000', '0.14621', '0.14662', '0.14578', '0.14656', '33498', '334980', '48981.5551', '1']
        history_k_line_300 = get_k_line(self.coin_name, cur_int_time_ms, self.time_mode) ##[new ... old] 300 result
        self.newest_300_history_price = []
        try:
            for i in range(298): ## 可能偶尔返回不了100个历史
                if history_k_line_300[i][-1]=="0": ##history_1m_k_line_100[i][-1] == "0":
                    continue ## newest does not finish
                else:
                    end_price = float(history_k_line_300[i][4])
                    self.newest_300_history_price.append(end_price) ##[new ... old]
            self.newest_300_history_price.reverse() ##[old ... new]
        except:
            # print("{} can not get 300 history".format(self.coin_name))
            return

        n = -5
        newest_n =  self.newest_300_history_price[n:]
        newest_sum = sum(newest_n)
        newest_num = len(newest_n)
        self.ma5 = newest_sum/newest_num

    def update_newest_15m_300_history(self):

        ## ['1729861200000', '0.14621', '0.14662', '0.14578', '0.14656', '33498', '334980', '48981.5551', '1']
        history_15m_k_line_300 = get_k_line(self.coin_name, cur_int_time_ms, "15m") ##[new ... old] 300 result
        self.newest_15m_300_history_price = []
        try:
            for i in range(298): ## 可能偶尔返回不了100个历史
                if history_15m_k_line_300[i][-1]=="0": ##history_1m_k_line_100[i][-1] == "0":
                    continue ## newest does not finish
                else:
                    end_price_15m = float(history_15m_k_line_300[i][4])
                    self.newest_15m_300_history_price.append(end_price_15m) ##[new ... old]
            self.newest_15m_300_history_price.reverse() ##[old ... new]
        except:
            # print("{} can not get 300 history".format(self.coin_name))
            return

        n = -60
        newest_n =  self.newest_15m_300_history_price[n:]
        newest_sum = sum(newest_n)
        newest_num = len(newest_n)
        self.m_stable = newest_sum/newest_num

        refer_before = self.newest_15m_300_history_price[-4*24*3:]
        self.refer = sum(refer_before)/len(refer_before)

        m = -30
        newest_m =  self.newest_15m_300_history_price[m:]
        newest_m_sum = sum(newest_m)
        newest_m_num = len(newest_m)
        self.m_trend = newest_m_sum/newest_m_num

        if self.init == 0:
            self.last_hit_m_stable = self.m_stable
            self.init = 1

        
        if self.price_hit(history_15m_k_line_300[1], self.m_stable):
            self.log += " newest_rng hit ma60  {}-{} {:8f}\n".format(history_15m_k_line_300[1][3], history_15m_k_line_300[1][2], self.m_stable)
            self.last_hit_m_stable = self.m_stable
        else:
            self.log += " newest_rng not hit ma60 : {} {}-{} {:8f}\n".format(time.ctime(int(history_15m_k_line_300[1][0][:-3])), history_15m_k_line_300[1][3], history_15m_k_line_300[1][2], self.m_stable)

    def get_self_config(self):
        try:
            self.burst   = config_dict[self.coin_name]["burst"]
            self.burst_1h= config_dict[self.coin_name]["burst_1h"]
            self.gain    = config_dict[self.coin_name]["gain"]
            self.loss    = config_dict[self.coin_name]["loss"]
            self.money_u = config_dict[self.coin_name]["money_u"]
            self.max_num = config_dict[self.coin_name]["max_num"]

            self.b_lever = config_dict[self.coin_name]["b_lever"]
            self.b_tdMode= config_dict[self.coin_name]["b_tdMode"]

            self.s_lever = config_dict[self.coin_name]["s_lever"]
            self.s_tdMode= config_dict[self.coin_name]["s_tdMode"]

            self.type    = config_dict[self.coin_name]["type"]
            self.hit_m_up= config_dict[self.coin_name]["hit_m_up"]
            self.hit_m_dn= config_dict[self.coin_name]["hit_m_dn"]
            self.withdraw= config_dict[self.coin_name]["withdraw"]
        except:
            self.burst   = config_dict["DEFAULT"]["burst"]
            self.burst_1h= config_dict["DEFAULT"]["burst_1h"]
            self.gain    = config_dict["DEFAULT"]["gain"]
            self.loss    = config_dict["DEFAULT"]["loss"]
            self.money_u = config_dict["DEFAULT"]["money_u"]
            self.max_num = config_dict["DEFAULT"]["max_num"]

            self.b_lever = config_dict["DEFAULT"]["b_lever"]
            self.b_tdMode= config_dict["DEFAULT"]["b_tdMode"]

            self.s_lever = config_dict["DEFAULT"]["s_lever"]
            self.s_tdMode= config_dict["DEFAULT"]["s_tdMode"]

            self.type    = config_dict["DEFAULT"]["type"]
            self.hit_m_up= config_dict["DEFAULT"]["hit_m_up"]
            self.hit_m_dn= config_dict["DEFAULT"]["hit_m_dn"]
            self.withdraw= config_dict["DEFAULT"]["withdraw"]

    def get_current_price(self):
        global all_cur_price
        for i in all_cur_price:
            ## i is inst dict
            if (self.coin_name+"-USDT-SWAP") == i["instId"]:
                ## i is the inst dict
                # print(i)
                return float(i["last"])

    def gen_current_parameter(self):
        self.get_self_config()
        self.cur_price = self.get_current_price()
        if len(self.newest_1m_history_price) == 0: ## if 1m do not have history, fill it with current price
            for i in range(20):
                self.newest_1m_history_price.append(self.cur_price)
        else:
            self.newest_1m_history_price.append(self.cur_price)
            self.newest_1m_history_price.pop(0)

        n = -5
        newest_n =  self.newest_1m_history_price[n:]
        newest_sum = sum(newest_n)
        newest_num = len(newest_n)
        self.ma5 = newest_sum/newest_num

        self.open_num = int(self.money_u * 5 // (self.ma5 * self.value))
        self.buy_long_burst   = (1-(self.burst) - max(prefer_idx,0))
        self.sell_short_burst = (1+(self.burst) - min(prefer_idx,0))
        self.buy_long_water_line   = 0 ##min(self.refer * self.buy_long_burst,   self.refer_1h_300 * (1-self.burst_1h))
        self.sell_short_water_line = 0 ##max(self.refer * self.sell_short_burst, self.refer_1h_300 * (1+self.burst_1h))

        # self.log += "[{}] ".format(cur_ctime) + self.coin_name + \
        #             " ma60: {:.8f}".format(self.ma5) + \
        #             " last_hit_m60: {:8f}".format(self.last_hit_m_stable) + \
        #             " 3day: {:.8f}".format(self.refer) + \
        #             " prefer: {:.5f}%".format(prefer_idx*100) + \
        #             " open_num: {:.5f}".format(self.open_num) + \
        #             " buy long water line: {:.5f} {:.3f}".format(self.buy_long_water_line, self.buy_long_burst) + \
        #             " sell short water line: {:.5f} {:.3f}".format(self.sell_short_water_line, self.sell_short_burst) + \
        #             " newest_10:{} \n".format(str(self.newest_15m_300_history_price[-10:]))

        self.log += "[{}] ".format(cur_ctime) + self.coin_name + \
                    " ma5: {:.8f}".format(self.ma5) + \
                    " prefer: {:.5f}%".format(prefer_idx*100) + \
                    " open_num: {:.5f}".format(self.open_num) + \
                    " buy long water line: {:.5f} {:.3f}".format(self.buy_long_water_line, self.buy_long_burst) + \
                    " sell short water line: {:.5f} {:.3f}".format(self.sell_short_water_line, self.sell_short_burst) + \
                    " newest_10:{} \n".format(str(self.newest_1m_history_price[-10:]))

    def get_current_status(self):
        global global_log
        global fill_order_list
        self.fill_id = []
        for i in fill_order_list:
            if (coin+"-USDT-SWAP") == i["instId"]:
                self.fill_id.append(i["ordId"])

        global position_list
        self.long_position_value = 0
        self.short_position_value = 0
        self.buy_long_position = []
        self.sell_short_position = []
        for i in position_list:
            if (coin+"-USDT-SWAP") == i["instId"]:
                if i["posSide"] == "short":
                    self.sell_short_position.append({"price":float(i["avgPx"]), "number":i["pos"]})
                    self.short_position_value = (float(i["avgPx"]) * float(i["pos"]) * self.value / 5)
                if i["posSide"] == "long":
                    self.buy_long_position.append({"price":float(i["avgPx"]), "number":i["pos"]})
                    self.long_position_value = (float(i["avgPx"]) * float(i["pos"]) * self.value / 5)
        # self.log += " [pos] long pos value:{:5f} short pos value:{:5f}\n".format(self.long_position_value, self.short_position_value)
                if self.short_position_value > 0:
                    global_log += "coin:{} hold short value:{} \n".format(coin,self.short_position_value)
                if self.long_position_value > 0:
                    global_log += "coin:{} hold long value:{} \n".format(coin,self.long_position_value)



    def cancel_order(self, order_id):
        result = tradeAPI.cancel_algo_order(
            params= [{ "algoId":order_id, "instId" : self.coin_name+"-USDT-SWAP"}]
        )
        if result["code"] == "0":
            # data = result["data"][0]
            # cl_ord_id = data["clOrdId"]
            self.log += "cancel order : orderid:{} \n".format(order_id)
            return 1
        else:
            self.log += "cancel fail: orderid: {} info: {} ".format(order_id, str(result))
            return 0

    def create_order(self, side, posSide, price, stop_gain_price, stop_loss_price, num):
        global global_log
        tdMode = self.b_tdMode if (posSide=="long") else self.s_tdMode
        lever  = self.b_lever  if (posSide=="long") else self.s_lever

        result = tradeAPI.place_algo_order(
            tdMode= tdMode, ## cross:全仓杠杆/永续 isolated:逐仓杠杆/永续 cash:非保证金币币
            ccy   ="USDT",
            side  =side,   ## 开多：buy long   开空：sell short   平多：sell long   平空：buy short
            posSide=posSide, 
            ordType="trigger", ## trigger:计划委托
            sz     = str(int(num) * lever / 5), ## 委托数量  /5是因为okx的币本位合约是5倍杠杆?

            triggerPx = price, ## 触发价格 
            orderPx   = "-1", ## 委托价格 , -1为市价

            attachAlgoOrds=[
                {
                    "tpTriggerPx":stop_gain_price,  ## 止盈触发价格
                    "tpOrdPx":stop_gain_price,# "-1",  ## 止盈委托价格 -1为市价
                    "slTriggerPx":stop_loss_price,  ## 止损触发价格
                    "slOrdPx":stop_loss_price #"-1"   ## 止损委托价格 -1为市价
                }
            ], ## 附带止盈止损

            instId =self.coin_name+"-USDT-SWAP"
        )

        if result["code"] == "0":
            data = result["data"][0]
            order_id = data["algoId"]
            self.log += "id:" + order_id + " " + side + " " + posSide + " create_success: " + \
                "price : " + str(price) + " stop : {} {} ".format(stop_gain_price, stop_loss_price) + "\n"
            return order_id
        else:
            self.log += "create_order_fail: " + str(result) + " open_price: " + str(price) + " num: " + str(num) + "\n"
            return ""

    def modify_order(self, order_id, price, stop_gain_price, stop_loss_price):
        result = tradeAPI.amend_algo_order(
            newTriggerPx =price,   ## 触发价格 
            newOrdPx     ="-1",   ## 委托价格 
            algoId       =order_id,  

            attachAlgoOrds=[
                {
                    "newTpTriggerPx":stop_gain_price,  ## 止盈触发价格
                    "newTpOrdPx":stop_gain_price,# "-1",  ## 止盈委托价格 -1为市价
                    "newSlTriggerPx":stop_loss_price,  ## 止损触发价格
                    "newSlOrdPx":stop_loss_price #"-1"   ## 止损委托价格 -1为市价
                }
            ], ## 附带止盈止损

            instId       =self.coin_name+"-USDT-SWAP"
        )
        if result["code"] == "0":
            data = result["data"][0]
            order_id = data["algoId"]
            self.log += "id:{} modify_success, new price {:5f} stop: {} {}\n".format(order_id, float(price), stop_gain_price, stop_loss_price)
            return order_id
        else: ## modify fail, cancel order
            # self.cancel_order(order_id)
            self.log += "modify_order_fail(need handle): id:{} new_price:{:5f} stop: {} {}".format(order_id, float(price), stop_gain_price, stop_loss_price) + str(result) + "\n"
            global global_log
            global_log += "{} {} modify_order_fail(need handle): id:{} new_price:{:5f} ".format(cur_ctime, self.coin_name, order_id, float(price)) + str(result) + "\n"
            
            self.cancel_order(order_id)
            # print(result)
            return ""

    def order_maintain(self, side, posSide, open_price, old_order_id, num): ## 20/2s
        stop_gain_price = "{:.9f}".format(open_price * ((1+float(self.gain)) if side=="buy" else (1-float(self.gain))))
        stop_loss_price = "{:.9f}".format(open_price * ((1-float(self.loss)) if side=="buy" else (1+float(self.loss))))
        open_price = "{:.9f}".format(open_price)
        need_create_modify_cond = 0
        water_line_ok = 0
        m_stable_ok = 0
        position_value_ok = 0
        if ((side=="buy") and (posSide=="long")):
            if (self.type >= 1):
                if num > 0:
                    # if (self.m_stable <= self.buy_long_water_line):
                    if (1):
                        # if (self.m_stable <= (self.last_hit_m_stable * self.hit_m_dn)):
                        if (1):
                            # if ((self.cur_price <= self.m_stable)):
                            if ((self.cur_price <= self.ma5)) or 1:
                                # if (self.m_trend >= (self.ma5*(1-self.withdraw))):
                                if (1):
                                    need_create_modify_cond = 1
                                else:
                                    self.log += "not stable , m_tread {} need {} ".format(self.m_trend, self.ma5*(1-self.withdraw))
                            else:
                                self.log += "cur_price > ma5 , should not create/modify "
                        else:
                            # self.log += "hit ma60 does not up enough   {:3f}% ".format((self.last_hit_m_stable / self.ma5 -1)*100)
                            pass
                    else:
                        self.log += "ma60 does not catch buy long water line   {:3f}% ".format((self.ma5 / self.buy_long_water_line -1)*100)
                else:
                    self.log += "money_u does not enough for a swap "
                position_value_ok = (2*self.long_position_value) < float(self.money_u * self.max_num)
            else:
                self.log += "type not allow. "
        elif ((side=="sell") and (posSide=="short")):
            if (self.type <= 1):
                if num > 0:
                    if (self.ma5 >= self.sell_short_water_line) or 1:
                        # if (self.ma5 >= (self.last_hit_m_stable * self.hit_m_up)) or 1:
                        if 1:
                            if (self.cur_price >= self.ma5) or 1:
                                # if (self.m_trend <= (self.ma5*(1+self.withdraw))) or 1:
                                if 1:
                                    need_create_modify_cond = 1
                                else:
                                    self.log += "not stable , m_tread {} need {} ".format(self.m_trend, self.ma5*(1+self.withdraw))        
                            else:
                                self.log += "cur_price < ma5, should not create/modify "
                        else:
                            # self.log += "hit ma60 does not down enough   {:3f}% ".format((self.ma5 / self.last_hit_m_stable -1)*100)
                            pass
                    else:
                        self.log += "ma60 does not catch sell short water line   {:3f}% ".format((self.sell_short_water_line / self.ma5 -1)*100)
                else:
                    self.log += "money_u does not enough for a swap "
                position_value_ok = (2*self.short_position_value) < float(self.money_u * self.max_num)
            else:
                self.log += "type not allow. "


        elif ((side=="sell") and (posSide=="long")):
            need_create_modify_cond = 1
            position_value_ok = 1
        elif ((side=="buy") and (posSide=="short")):
            need_create_modify_cond = 1
            position_value_ok = 1
        else:
            pass

        if need_create_modify_cond:
            if old_order_id == "": ## no order, create new
                if position_value_ok:
                    open_order_id = self.create_order(side, posSide, open_price, stop_gain_price, stop_loss_price, num)
                    return open_order_id
                else:
                    self.log += "too more order, not create order\n" 
                    return ""
            if old_order_id in self.fill_id:  ## fill, should create
                if position_value_ok:
                    self.log += "fill, need create new one. "
                    open_order_id = self.create_order(side, posSide, open_price, num)
                    return open_order_id
                else:
                    self.log += "too more order, not create order\n" 
                    return ""

            modify_order_id = self.modify_order(old_order_id, open_price, stop_gain_price, stop_loss_price)
            return modify_order_id

        else: ## not meet cond, cancel it
            if old_order_id != "":
                self.cancel_order(old_order_id)
            self.log += "\n"
            return ""

    buy_long_id  = ""
    sell_short_id = ""
    sell_long_id  = ""
    buy_short_id = ""
    def run(self, flag_15m = 0): ## 0:1m  1:15m  ## run is the 1st function when a period run
        self.flag_15m = flag_15m
        self.gen_current_parameter()
        self.get_current_status()

        # self.log += " [sell long ] "  ## 平多
        # if len(self.buy_long_position):
        #     price = self.buy_long_position[0]["price"]
        #     num   = self.buy_long_position[0]["number"]
        #     if (self.ma5/price >= (1+float(self.gain))) or 1:
        #         self.log += "try sell long hold_price:{} num:{} ".format(price, num)
        #         self.sell_long_id = self.order_maintain("sell", "long", price * (1 + float(self.gain)), self.sell_long_id, num)
        #     else:
        #         self.log += "fail sell long hold:{} num:{}, ma60 target {:5f} \n".format(price, num, price*(1+float(self.gain)))
        # else:
        #     self.log += "does not hold\n"

        # self.log += " [buy short ] "  ## 平空
        # if len(self.sell_short_position):
        #     price = self.sell_short_position[0]["price"]
        #     num   = self.sell_short_position[0]["number"]
        #     if (self.ma5/price <= (1-float(self.gain))) or 1:
        #         # print("try buy short {} {}".format(price, number))
        #         self.log += "try buy short hold_price:{:5f} num:{} ".format(price, num)
        #         self.buy_short_id = self.order_maintain("buy", "short", price * (1 - float(self.gain)), self.buy_short_id, num)
        #     else:
        #         self.log += "fail buy short hold:{:5f} num:{}, ma60 target {:5f} \n".format(price, num, price*(1-float(self.gain)))
        #         # print("fail buy short {} {}, target {}".format(price, num, price*(1-float(self.gain))))
        # else:
        #     self.log += "does not hold\n"


        self.log += " [buy long  ] "  ## 开多
        self.buy_long_id   = self.order_maintain("buy", "long",   self.ma5 * (1-float(self.burst)), self.buy_long_id, self.open_num)


        self.log += " [sell short] "  ## 开空
        self.sell_short_id = self.order_maintain("sell", "short", self.ma5 * (1+float(self.burst)), self.sell_short_id, self.open_num)


    def write_log(self):
        log_info(self.log, "./log/run_log/{}.log".format(self.coin_name))
        self.log = ""


    def cancel_open_order(self):
        self.cancel_order(self.buy_long_id)
        self.cancel_order(self.sell_short_id)
        self.cancel_order(self.sell_long_id )
        self.cancel_order(self.buy_short_id )

    ## when finish make order, update the newest kline history
    def back_call(self):
        # self.update_newest_15m_300_history()
        # self.update_newest_1h_300_history()
        # self.update_newest_300_history()
        self.write_log()

def interval_sleep(max_operate = 10):  ## max_operate means operate per second
    global sleep_counter
    sleep_counter += 1
    if sleep_counter >= max_operate:
        time.sleep(1)
        sleep_counter = 0


## create a BTC order to make sure the script is working
def create_working_order():
    result = tradeAPI.place_algo_order(
        tdMode="isolated", ## cross:全仓杠杆/永续 isolated:逐仓杠杆/永续 cash:非保证金币币
        ccy   ="USDT",
        side  ="buy",   ## 开多：buy long   开空：sell short   平多：sell long   平空：buy short
        posSide="long", 
        ordType="trigger",
        sz     = "1", ## 委托数量

        triggerPx = "1", ## 触发价格 
        orderPx   = "-1", ## 委托价格 , -1为市价
        instId ="BTC-USDT-SWAP"
    )

    if result["code"] == "0":
        print("working...")
        data = result["data"][0]
        order_id = data["algoId"]
        return order_id
    else:
        print("create working order fail")
        exit(0)


if __name__ == "__main__":
    time_mode = "1m"  ## 1m or 15m

    back_test = 0
    global_log = ""

    config_dict = get_config()
    coin_list = config_dict.keys()
    all_coins = get_all_swap_list()
    # all_coins = ["WLFI","CFX","DOGE","PUMP","OKB","PEPE","LINEA","SKY"] ## only for test
    # all_coins = ["SHIB"] ## only for test
    public_data = get_public_data()

    cur_int_time_s = get_current_system_time(ms=0, int_value=1)
    cur_int_time_ms = str(cur_int_time_s)+"000"
    cur_ctime = time.ctime(cur_int_time_s)

    coin_obejcts = {}
    sleep_counter = 0
    prefer_idx = 0
    for coin_name in all_coins:
        coin_obj = Coin(coin_name, time_mode)
        if time_mode == "1m":
            coin_obejcts[coin_name] = coin_obj ##Coin(coin_name)
        else:
            if len(coin_obj.newest_300_history_price) > 295: ## make sure 300 history get ok
                coin_obejcts[coin_name] = coin_obj ##Coin(coin_name)
        interval_sleep(5) ## set leverage 20/2s
    print("initial done")
    working_id = create_working_order()
    while 1:
        try:
        # if 1:
            cur_int_time_s = get_current_system_time(ms=0, int_value=1)
            cur_int_time_ms = str(cur_int_time_s)+"000"
            cur_ctime = time.ctime(cur_int_time_s)

            # coin_list = config_dict.keys()
            # for coin_name in all_coins:
            #     if coin_name in coin_obejcts.keys():
            #         pass
            #     else:
            #         public_data = get_public_data()
            #         coin_obejcts[coin_name] = Coin(coin_name)

            # unfinish_order_list = get_unfinish_order()
            fill_order_list = get_fills()
            position_list   = get_current_positions()
            all_cur_price   = get_all_swap_current_price()

            # if len(fill_order_list) == 0: ## to detect the script is on working
            #     create_working_order()
            #     global_log += cur_ctime + " create working order\n"


            for coin in coin_obejcts.keys():
                coin_obejcts[coin].run()
                if time_mode == "1m":
                    pass
                else:
                    interval_sleep(40)
            global_log += cur_ctime + " finish all older\n"

            total_hold = 0
            merge_hold = 0
            for coin in coin_obejcts.keys():
                coin_obejcts[coin].back_call()
                # total_hold += coin_obejcts[coin].short_position_value
                # total_hold += coin_obejcts[coin].long_position_value
                # merge_hold -= coin_obejcts[coin].short_position_value
                # merge_hold += coin_obejcts[coin].long_position_value
                if time_mode == "1m":
                    pass
                else:
                    interval_sleep(10)

            if total_hold == 0:
                prefer_idx = 0
            else:
                prefer_idx =  merge_hold / config_dict["DEFAULT"]["total_u"]

            global_log += "total:{} merge:{} \n".format(total_hold,merge_hold)
            config_dict = get_config()

            global_log += "sleep"
            log_info(global_log, "./log/run_log/111_global_log.log")
            global_log = ""

            cur_int_time_s = get_current_system_time(ms=0, int_value=1)
            cur_ctime = time.ctime(cur_int_time_s)
            time_flag_per_minite(cur_ctime, time_mode)

        # elif 0:
        except KeyboardInterrupt:
            print("kill and cancel order")
            for coin in coin_obejcts.keys():
                log_info(coin_obejcts[coin].log, "./log/run_log/{}.log".format(coin))
                coin_obejcts[coin].cancel_open_order()
                interval_sleep(20)
            tradeAPI.cancel_algo_order( params= [{ "algoId":working_id, "instId" : "BTC-USDT-SWAP"}])
            log_info(cur_ctime + " some exception\n", "./log/run_log/{}.log".format(coin))
            break
        except Exception as e:
        # else:
            print("some exception, need handle and exit")
            tradeAPI.cancel_algo_order( params= [{ "algoId":working_id, "instId" : "BTC-USDT-SWAP"}])
            print(e)
            break
    exit(0)

