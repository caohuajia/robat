import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime
import joblib

class KLine(object):
    def __init__(self, name):
        self.name = name
        self.trade_history = []
        self.float_money_list = []
        
        self.change_list = []
        self.last_change = 0
        self.k_line_list = []
        self.x_lables = []
        self.ma30_list = []
        self.ma60_list = []
        self.ma300_list = []

# 输出：Mon Oct  6 17:15:00 2025    ->  10/06 17:15
def simplify_time(time_str):
    dt = datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
    return dt.strftime("%m/%d %H:%M")

def show_hist(change_list):
    # change_list = [0,0,0,0,0,1,1,1,1,2,2,3,4,5,6,9]
    # 绘制直方图
    custom_bins = np.arange(-400, 400) ## -4% ~ 4%
    plt.hist(change_list, bins=custom_bins,)

    # 添加标题和标签
    plt.title('Histogram Example')
    plt.xlabel('Value')
    plt.ylabel('Frequency')

    # 显示图表
    plt.show()

def show_k_line(kline):
    ypoints = np.array(kline.k_line_list)
    x = range(len(ypoints))

    fig, ax = plt.subplots()

    def on_mouse_move(event):
        if event.inaxes == ax:  # 仅在当前坐标轴范围内触发
            x_val = event.xdata
            y_val = event.ydata
            x_txt = kline.x_lables[int(x_val)] if 0 <= int(x_val) < len(kline.x_lables) else ''
            y_txt = ypoints[int(x_val)] if 0 <= int(x_val) < len(ypoints) else ''
            # ax.set_title(f"x: {x_val:.2f}, y: {y_val:.2f}")  # 更新标题显示
            ax.set_title(f"x: {x_txt}, y: {y_txt}")  # 更新标题显示
            fig.canvas.draw_idle()  # 重绘图形
    fig.canvas.mpl_connect('motion_notify_event', on_mouse_move)

    plt.xticks(ticks=x, labels=kline.x_lables)

    if len(kline.trade_history) > 0:
        for trade in kline.trade_history:
            begin_cnt = trade["begin_cnt"]
            begin_price = trade["price"]
            end_cnt = trade["deal_cnt"]
            end_price = trade["deal_price"]
            if trade["blow"] == 1:
                ax.annotate('', xy=(end_cnt, end_price), xytext=(begin_cnt, begin_price), arrowprops=dict(arrowstyle='->', color='green'))
            else:
                ax.annotate('', xy=(end_cnt, end_price), xytext=(begin_cnt, begin_price), arrowprops=dict(arrowstyle='->', color='red'))


    ax.xaxis.set_major_locator(ticker.AutoLocator())  # 自动设置主刻度位置
    # ax.xaxis.set_major_locator(mdates.DayLocator())  # 自动设置主刻度位置
    # ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))  # 设置日期格式
    ax.yaxis.set_major_locator(ticker.AutoLocator())  # 自动设置主刻度位置
    # ma5 = np.array(k_line_list)

    plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.3)
    plt.title(kline.name)
    plt.plot(ypoints, marker='', label=kline.name, linewidth=0.7)
    plt.plot(np.array(kline.ma30_list), marker='', label="ma30", linewidth=0.5)
    plt.plot(np.array(kline.ma60_list), marker='', label="ma60", linewidth=0.5)
    plt.plot(np.array(kline.ma300_list), marker='', label="ma300", linewidth=0.5)



    # ax2 = ax.twinx()
    # ax2.plot(x, np.array(kline.float_money_list), marker='', label='float money', linewidth=0.6, color='r')
    # ax2.set_ylabel('float money', color='r')
    # ax2.set_ylim(ymin=0)  # Y轴范围为0到100


    plt.legend()
    # plt.plot(ma5, marker='x')


total_days = 1 + 30
# interval = "15m"
interval = "1m"
test_one = 1
# test_coin = "11test"
test_coin = "DOGE"
test_coin = "OKB"
test_coin = "CETUS"
# test_coin = "BTC"
# test_coin = "aa_data2"
# test_coin = "aa_data1"

# all_coins = get_all_swap_list()
all_coins = ["nop"]
# btc_change_list = get_change_list("BTC")
# eth_change_list = get_change_list("ETH")

all_coin_struct = {}
for one_coin in all_coins:
    if test_one:
        one_coin = test_coin
    
    kline = KLine(one_coin)

    kline.trade_history = joblib.load("./log/{}_trade_history.sva".format(one_coin))
    # for i in kline.trade_history:
    #     print(i)
    kline.float_money_list = joblib.load("./log/{}_float_money_list.sva".format(one_coin))


    with open("./data/{}/{}days/{}_price.json".format(interval, str(total_days), one_coin), "r") as f:
        k_line_history = json.load(f)
        # print(len(k_line_history))
        # print(k_line_history[0:5])
        for piece in k_line_history:
            time_str = simplify_time(piece[0])
            kline.x_lables.append(time_str)
            begin_price = float(piece[1])
            end_price = float(piece[4])
            kline.k_line_list.append(end_price)
            kline.ma30_list.append(np.average(kline.k_line_list[-30:]))
            kline.ma60_list.append(np.average(kline.k_line_list[-60:]))
            kline.ma300_list.append(np.average(kline.k_line_list[-300:]))
            change = int((end_price / begin_price - 1) * 100 * 100) ## 0.01%

            if change != 0:
                if kline.last_change < -10: ## 0.01%
                    kline.change_list.append(change)
            kline.last_change = change
    # print(np.average(kline.change_list))
    # print(kline.change_list)
    # show_hist(kline.change_list)
    show_k_line(kline) ## 绘制end price
    plt.show()

    if test_one:
        break
