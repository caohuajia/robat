import time
import json
from base_okx import *
from coins import *

def create_order(coin, price, number, side, posSide, tp_px):
    global cur_ctime
    result = tradeAPI.place_order(
        tdMode="cross", ## cross:全仓杠杆/永续 isolated:逐仓杠杆/永续 cash:非保证金币币
        ccy   ="USDT",
        side  =side,   ## 开多：bug long   开空：sell short   平多：sell long   平空：bug short
        posSide=posSide, 
        ordType="limit", ## 限价：limit 市价：market
        sz     =str(number), ## 委托数量
        px     =price,   ## 委托价格 
        # attachAlgoOrds=1,
        tpTriggerPx=tp_px,
        tpOrdPx    =tp_px,
        # tpOrdKind  ="limit",
        clOrdId="",  ## 自定义订单id
        instId =coin
    )
    if result["code"] == "0":
        data = result["data"][0]
        order_id = data["ordId"]
        info = "["+cur_ctime + "] " + coin + " id:" + order_id + " " + side + " " + posSide + " create_success: " + \
               "price : " + price + " ->| " + tp_px
        log_info(info)
        # print(info )
        return order_id
    else:
        info = "["+cur_ctime + "] " + "create_order_fail: " + str(result)
        log_info(info)
        print(result)

def modify_order(coin, order_id, price, tp_px):
    global cur_ctime
    result = tradeAPI.amend_order(
        newPx  =price,   ## 委托价格 
        ordId  =order_id,  
        # attachAlgoOrds=1,
        newTpTriggerPx=tp_px,
        newTpOrdPx    =tp_px,
        # newTpOrdOx    ="limit",
        instId =coin
    )
    if result["code"] == "0":
        data = result["data"][0]
        order_id = data["ordId"]
        info = "["+cur_ctime + "] " + coin + " id:" + order_id + " " + " modify_success: " + \
               "price : " + price + " ->| " + tp_px
        log_info(info)
        # print(info )
        return order_id
    else:
        info = cur_ctime + " " + "modify_order_fail: " + str(result)
        log_info(info)
        print(result)

def cancel_order(coin):
    global cur_ctime
    result = tradeAPI.cancel_order(
        clOrdId="1",
        instId =(coin+"-USDT-SWAP")
    )
    if result["code"] == "0":
        data = result["data"][0]
        cl_ord_id = data["clOrdId"]
        print(cur_ctime, coin + " cancel order : " + "orderid: " + cl_ord_id )
    else:
        print("cancen fail: ", result)



def time_flag_per_minite():
    global cur_ctime
    cur_clock_str = cur_ctime.split(" ")[-2]
    cur_sec = cur_clock_str[-2:]
    cur_min = cur_clock_str[-5:-3]
    cur_sec_int = int(cur_sec)
    time.sleep(60 - cur_sec_int)

    if cur_min == "14" or cur_min == "29" or cur_min == "44" or cur_min == "59":
        return 2
    else:
        return 1

init_state = 1
price_list_dict = {}
def maintain_price_list_dict(coin_list):
    global init_state
    global price_list_dict

    if init_state:
        for i,coin in enumerate(coin_list):
            price_list = []
            ##['1728006240000', '0.15846', '0.15859', '0.15785', '0.15785', '4480', '44800', '7090.9912', '0']
            k_line_100_history = get_k_line(coin, "1m") ##[new ... old]
            for i in range(80): ## 可能偶尔返回不了100个历史
                if 0: ##k_line_100_history[i][-1] == "0":
                    continue ## newest does not finish
                else:
                    end_price = k_line_100_history[i][4]
                    price_list.append(float(end_price)) ##[new ... old]
            price_list.reverse() ##[old ... new]
            if (i % 10) == 9:
                time.sleep(1) ## aovid too frequetly api use, 10/s
            price_list_dict[coin] = price_list
        init_state = 0
    else:
        pass
    time_flag = time_flag_per_minite() ## 1 min

    for coin in coin_list:
        price_list_in_dict = price_list_dict[coin]
        price_list_in_dict.pop(0)
        price_list_in_dict.append(float(get_current_swap_price(coin)))
        price_list_dict[coin] = price_list_in_dict
    
    return price_list_dict

def order_control(coin, side, posSide, open_price ,open_num, tp_px, old_order_id, unfinish_id, unfinish_order_num):
    global cur_ctime
    open_price = "{:.9f}".format(open_price)
    tp_px      = "{:.9f}".format(tp_px)
    ## modify
    if old_order_id != "":
        if old_order_id in unfinish_id:  ## modify
            modify_order_id = modify_order(coin, old_order_id, open_price, tp_px)
            return modify_order_id
        else:  ## unknown, modify fail, means deal. So does not return, buy a new one
            log =  "["+cur_ctime + "] id:" + old_order_id + " modify fail"
            log_info(log)

    ## buy
    if unfinish_order_num <= 6:
        open_order_id = create_order(coin, open_price, open_num, side, posSide, tp_px)
    else:
        log = coin = " order num > 6, not create order"
        log_info(log)
    return open_order_id


def trade_strategy():
    global coin_property
    global cur_ctime
    coin_list = coin_property.keys()
    cur_run_order_id = {}
    for coin in coin_list:
        coin_run_info = {}
        coin_run_info["ma5_open_more_id"] = ""
        coin_run_info["ma5_open_empy_id"] = ""
        coin_run_info["ma15_open_more_id"] = ""
        coin_run_info["ma15_open_empy_id"] = ""

        cur_run_order_id[coin] = coin_run_info


    while(1):
        cur_ctime = time.ctime(get_current_system_time(ms=0, int_value=1))
        newest_history_price_dict = maintain_price_list_dict(coin_list) ## 1 min
        unfinish_order_list = get_unfinish_order()

        for coin in coin_list:
            newest_80_history_price = newest_history_price_dict[coin]
            burst   = coin_property[coin]["burst"]
            money_u = coin_property[coin]["money_u"]
            open_num = int(money_u // newest_80_history_price[-1])
            ma5 = sum(newest_80_history_price[-5:])/5
            ma15_list = []
            for i in range(15):
                ma15 = sum(newest_80_history_price[0+i:15+i])/15
                ma15_list.append(ma15)

            ma_15_max = max(ma15_list)
            ma_15_min = min(ma15_list)

            ma5_open_more_price = ma5 * (1-burst)
            ma5_open_empy_price = ma5 * (1+burst)
            ma5_open_more_stop  = ma5_open_more_price * (1+burst)
            ma5_open_empy_stop  = ma5_open_empy_price * (1-burst)

            ma15_open_more_price = ma_15_min * 0.95
            ma15_open_empy_price = ma_15_max * 1.05
            ma15_open_more_stop  = ma15_open_more_price * 1.05
            ma15_open_empy_stop  = ma15_open_empy_price * 0.95

            ## sell
            unfinish_id = []
            unfinish_order_num = 0
            for i in unfinish_order_list:
                if (coin+"-USDT-SWAP") == i["instId"]:
                    unfinish_id.append(i["ordId"])
                    unfinish_order_num += 1

            log = "unfinish price & id: " + str(ma5_open_more_price) + " " + str(ma5_open_empy_price) + " " + \
                                str(ma5_open_more_price) + " " + str(ma5_open_empy_price) + " " +str(unfinish_order_list) + " "
            

            log_info("\n" + log)

            ma5_open_more_id = cur_run_order_id[coin]["ma5_open_more_id"]
            ma5_open_empy_id = cur_run_order_id[coin]["ma5_open_empy_id"]

            ma5_open_more_id = order_control(coin+"-USDT-SWAP", "buy",  "long",  ma5_open_more_price, open_num,\
                                             ma5_open_more_stop, ma5_open_more_id, unfinish_id, unfinish_order_num)
            ma5_open_empy_id = order_control(coin+"-USDT-SWAP", "sell", "short", ma5_open_empy_price, open_num,\
                                             ma5_open_empy_stop, ma5_open_empy_id, unfinish_id, unfinish_order_num)

            cur_run_order_id[coin]["ma5_open_more_id"] = ma5_open_more_id
            cur_run_order_id[coin]["ma5_open_empy_id"] = ma5_open_empy_id

            log1 = "["+cur_ctime + "] " + coin +" ma5:" + str(ma5) + " ma15_max:" + str(ma_15_max) + " ma15_min:" + str(ma_15_min) \
                                    +  " ma15_list:" + str(ma15_list) + "\n"
            log2 = " ma5 open more: "   + str(ma5_open_more_price) +  " ->| " + str(ma5_open_more_stop) + " open_num: " + str(open_num) +\
                   " ma5 open empty: "  + str(ma5_open_empy_price) +  " ->| " + str(ma5_open_empy_stop) + \
                   " ma15 open more: "  + str(ma15_open_more_price) + " ->| " + str(ma15_open_more_stop)   + \
                   " ma15 open empty: " + str(ma15_open_empy_price) + " ->| " + str(ma15_open_more_stop)   + \
                   " newest_80: " + str(newest_80_history_price)
            log_info(log1+log2)
            # print(ma5,ma15_list)

if __name__ == "__main__":
    trade_strategy()
    exit(0)

