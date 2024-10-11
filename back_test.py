import time
import json
from base_okx import *

def back_test():
    coin = "CETUS"
    k_line_100_history = get_k_line(coin,"1m")
    k_line_100_history.reverse()
    end_price = 0
    end_price_list= []
    benefit = 0
    open_more_order_list = []

    for i in range(len(k_line_100_history)-1):
        cur_history_picec = k_line_100_history[i]
        end_price  = cur_history_picec[4]
        if i < 30:
            pass
        else:
            ma5 = sum(end_price_list[-5:])/5
            ma5_open_more_price = ma5 * 0.99
            ma5_open_empy_price = ma5 * 1.01
            open_more_order_num = len(open_more_order_list)
            if open_more_order_num > 0:
                for hold_price in open_more_order_list:
                    if price_can_trade(hold_price * 1.01, cur_history_picec):
                        benefit += 0.1
                        open_more_order_list.remove(hold_price)
                        print(time.ctime(change_time_type(cur_history_picec[0], ms=0, int_value=1)) + " sell price: " + str(hold_price * 1.01) + " benefit: " + str(benefit))
            if open_more_order_num <=10:
                if price_can_trade(ma5_open_more_price, cur_history_picec):
                    open_more_order_list.append(ma5_open_more_price)
                    print(time.ctime(change_time_type(cur_history_picec[0], ms=0, int_value=1)) + " open more price: " + str(ma5_open_more_price) + " ma5: " + str(ma5))
            else:
                pass
            end_price_list.pop(0)
        
        end_price_list.append(float(end_price))
    print(open_more_order_list)


if __name__ == "__main__":
    pass