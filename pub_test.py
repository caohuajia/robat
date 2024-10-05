import time
import json
from base_okx import *

def create_order(price, number, side, posSide, tp_px):
    global global_order_id
    # product_type = "PEPE-USDT-SWAP"
    product_type = "CETUS-USDT-SWAP"
    result = tradeAPI.place_order(
        tdMode="cross", ## cross:全仓杠杆/永续 isolated:逐仓杠杆/永续 cash:非保证金币币
        side  =side,   ## 开多：bug long   开空：sell short   平多：sell long   平空：bug short
        posSide=posSide, 
        ordType="limit", ## 限价：limit 市价：market
        sz     =str(number), ## 委托数量
        px     =str(price),   ## 委托价格 
        # attachAlgoOrds=1,
        tpTriggerPx=str(tp_px),
        tpOrdPx    =str(tp_px),
        # tpOrdKind  ="limit",
        clOrdId="",  ## 自定义订单id
        instId =product_type
    )
    if result["code"] == "0":
        data = result["data"][0]
        order_id = data["ordId"]
        info = "["+time.ctime(get_current_system_time(ms=0, int_value=1)) + "] " + product_type + " id:" + order_id + " " + side + " " + posSide + " create_success: " + \
               "price : " + str(price) + " ->| " + str(tp_px)
        log_info(info)
        # print(info )
        return order_id
    else:
        info = "["+time.ctime(get_current_system_time(ms=0, int_value=1)) + "] " + "create_order_fail: " + str(result)
        log_info(info)
        print(result)

def modify_order(order_id, price, tp_px):
    # product_type = "PEPE-USDT-SWAP"
    product_type = "CETUS-USDT-SWAP"
    result = tradeAPI.amend_order(
        newPx  =str(price),   ## 委托价格 
        ordId  =order_id,  
        # attachAlgoOrds=1,
        newTpTriggerPx=str(tp_px),
        newTpOrdPx    =str(tp_px),
        # newTpOrdOx    ="limit",
        instId =product_type
    )
    if result["code"] == "0":
        data = result["data"][0]
        order_id = data["ordId"]
        info = "["+time.ctime(get_current_system_time(ms=0, int_value=1)) + "] " + product_type + " id:" + order_id + " " + " modify_success: " + \
               "price : " + str(price) + " ->| " + str(tp_px)        
        log_info(info)
        # print(info )
        return order_id
    else:
        info = time.ctime(get_current_system_time(ms=0, int_value=1)) + " " + "modify_order_fail: " + str(result)
        log_info(info)
        print(result)

def cancel_order():
    product_type = "CETUS-USDT-SWAP"
    result = tradeAPI.cancel_order(
        clOrdId="1",
        instId =product_type
    )
    if result["code"] == "0":
        data = result["data"][0]
        cl_ord_id = data["clOrdId"]
        print(time.ctime(get_current_system_time(ms=0, int_value=1)), 
              product_type + " cancel order : " + "orderid: " + cl_ord_id )
    else:
        print("cancen fail: ", result)



def time_flag_per_minite():
    cur_ctime = time.ctime(get_current_system_time(ms=0, int_value=1)) ## Thu Oct  3 20:56:01 2024
    cur_clock_str = cur_ctime.split(" ")[-2]
    cur_sec = cur_clock_str[-2:]
    cur_min = cur_clock_str[-5:-3]
    cur_sec_int = int(cur_sec)
    # print(cur_ctime)
    time.sleep(60 - cur_sec_int)
    # print(time.ctime(get_current_system_time(ms=0, int_value=1)))

    if cur_min == "14" or cur_min == "29" or cur_min == "44" or cur_min == "59":
        return 2
    else:
        return 1

init_state = 1
price_list = []
def maintain_price_list():
    global init_state
    global price_list

    if init_state:
        ##['1728006240000', '0.15846', '0.15859', '0.15785', '0.15785', '4480', '44800', '7090.9912', '0']
        k_line_100_history = get_k_line("1m") ##[new ... old]
        for i in range(50): ## 可能偶尔返回不了100个历史
            if 0: ##k_line_100_history[i][-1] == "0":
                continue ## newest does not finish
            else:
                end_price = k_line_100_history[i][4]
                price_list.append(float(end_price)) ##[new ... old]
        price_list.reverse() ##[old ... new]
        init_state = 0
    else:
        pass
    time_flag = time_flag_per_minite() ## 1 min

    price_list.pop(0)
    price_list.append(float(get_current_price()))
    
    return price_list[-30:]

def order_control(side, posSide, open_price, tp_px, old_order_id, unfinish_id, unfinish_order_num):
    open_num = 100
    ## modify
    if old_order_id != "":
        if old_order_id in unfinish_id:  ## modify
            modify_order_id = modify_order(old_order_id, open_price, tp_px)
            return modify_order_id
        else:  ## unknown
            log =  "["+time.ctime(get_current_system_time(ms=0, int_value=1)) + "] id:" + old_order_id + " modify fail"
            log_info(log)

    ## buy
    if unfinish_order_num < 10:
        open_order_id = create_order(open_price, open_num, side, posSide, tp_px)
    return open_order_id


def trade_strategy():
    ma5_open_more_id  = ""
    ma5_open_empy_id  = ""
    ma15_open_more_id = ""
    ma15_open_empy_id = ""
    ma5_open_more_id_list  = []

    old_ma5_open_more_price = 0
    old_ma5_open_empy_price = 0
    old_ma15_open_more_price = 0
    old_ma15_open_empy_price = 0

    ma5_open_more_price = 0
    ma5_open_empy_price = 0
    ma15_open_more_price = 0
    ma15_open_empy_price = 0

    while(1):
        newest_30_price = maintain_price_list() ## 1 min

        ma5 = sum(newest_30_price[-5:])/5
        ma15_list = []
        for i in range(15):
            ma15 = sum(newest_30_price[0+i:15+i])/15
            ma15_list.append(ma15)

        ma_15_max = max(ma15_list)
        ma_15_min = min(ma15_list)

        ma5_open_more_price = ma5 * 0.99
        ma5_open_empy_price = ma5 * 1.01
        ma5_open_more_stop  = ma5_open_more_price * 1.01
        ma5_open_empy_stop  = ma5_open_empy_price * 0.99

        ma15_open_more_price = ma_15_min * 0.95
        ma15_open_empy_price = ma_15_max * 1.05
        ma15_open_more_stop  = ma15_open_more_price * 1.05
        ma15_open_empy_stop  = ma15_open_empy_price * 0.95

        ## sell
        unfinish_order = get_unfinish_order()
        unfinish_id = []
        unfinish_order_num = len(unfinish_order)
        for i in unfinish_order:
            unfinish_id.append(i["ordId"])
        
        log = "unfinish price & id: " + str(ma5_open_more_price) + " " + str(ma5_open_empy_price) + " " + \
                              str(ma5_open_more_price) + " " + str(ma5_open_empy_price) + " " +str(unfinish_id) + " "
        

        log_info("\n" + log)

        ma5_open_more_id = order_control("buy",  "long",  ma5_open_more_price, ma5_open_more_stop, ma5_open_more_id, unfinish_id, unfinish_order_num)
        ma5_open_empy_id = order_control("sell", "short", ma5_open_empy_price, ma5_open_empy_stop, ma5_open_empy_id, unfinish_id, unfinish_order_num)

        log1 = "["+time.ctime(get_current_system_time(ms=0, int_value=1)) + "] ma5:" + str(ma5) + " ma15_max:" + str(ma_15_max) + " ma15_min:" + str(ma_15_min) \
                                +  " ma15_list:" + str(ma15_list) + "\n"
        log2 = " ma5 open more: "   + str(ma5_open_more_price) +  " ->| " + str(ma5_open_more_stop) + \
               " ma5 open empty: "  + str(ma5_open_empy_price) +  " ->| " + str(ma5_open_empy_stop) + \
               " ma15 open more: "  + str(ma15_open_more_price) + " ->| " + str(ma15_open_more_stop)   + \
               " ma15 open empty: " + str(ma15_open_empy_price) + " ->| " + str(ma15_open_more_stop)   + \
               " newest_30: " + str(newest_30_price)
        log_info(log1+log2)
        # print(ma5,ma15_list)

if __name__ == "__main__":
    trade_strategy()
    exit(0)

