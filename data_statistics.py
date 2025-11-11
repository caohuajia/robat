import json
import matplotlib.pyplot as plt
import numpy as np

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

def show_k_line(k_line_list):
    ypoints = np.array(k_line_list)
    # ma5 = np.array(k_line_list)

    plt.plot(ypoints, marker='')
    # plt.plot(ma5, marker='x')


total_days = 1 + 30
interval = "15m"
# interval = "1m"
test_one = 1
# test_coin = "11test"
test_coin = "DOGE"
test_coin = "OKB"
# test_coin = "aa_data2"
# test_coin = "aa_data1"

# all_coins = get_all_swap_list()
all_coins = ["8888"]
# btc_change_list = get_change_list("BTC")
# eth_change_list = get_change_list("ETH")

all_coin_struct = {}
for one_coin in all_coins:
    if test_one:
        one_coin = test_coin

    change_list = []
    last_change = 0
    k_line_list = []
    ma30_list = []
    with open("./data/{}/{}days/{}_price.json".format(interval, str(total_days), one_coin), "r") as f:
        k_line_history = json.load(f)
        # print(len(k_line_history))
        # print(k_line_history[0:5])
        for piece in k_line_history:
            begin_price = float(piece[1])
            end_price = float(piece[4])
            k_line_list.append(end_price)
            ma30_list.append(np.average(k_line_list[-90:]))
            change = int((end_price / begin_price - 1) * 100 * 100) ## 0.01%

            if change != 0:
                if last_change < -10: ## 0.01%
                    change_list.append(change)
            last_change = change
    print(np.average(change_list))
    # print(change_list)
    # show_hist(change_list)
    show_k_line(k_line_list)
    plt.show()

    if test_one:
        break
