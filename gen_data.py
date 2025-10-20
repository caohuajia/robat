##  timestap         begin      highest    lowest     end                                      complete
## ['1729861200000', '0.14621', '0.14662', '0.14578', '0.14656', '33498', '334980', '48981.5551', '1']

import matplotlib.pyplot as plt
import numpy as np
import json

pattern        = []
for i in range(20):
    pattern.append(100)
for i in range(20):
    pattern.append(150)
change_pattern = []
for i in range(20):
    change_pattern.append(3)
for i in range(20):
    change_pattern.append(-0.2)

def get_ma_n(lst, n):
    if len(lst) < n:
        return sum(lst)/len(lst)
    else:
        return sum(lst[-n:])/n

def get_fft(newest_100, N=100):    ## 
    fft_result = np.fft.fft(newest_100)
    freqs = np.fft.fftfreq(N, 1/N)
    fft_result = fft_result[:N//2]
    freqs = freqs[:N//2]
    amplitude = np.abs(fft_result)
    fre_list = []
    for i in range(N//2):
        if (amplitude[i]/N*2) > 0.01:
            fre_list.append(amplitude[i]/N*2)
            # print("{}:{:5f} ".format(i,amplitude[i]/N*2),end="")
    # print("")
    return fre_list

def gen_data(file_name, num_points):
    file_path = './data/15m/31days/{}_price.json'.format(file_name)
    all_pieces = []
    with open(file_path, 'w') as f:
        time_step = 0
        last_end = 100
        end_points = []
        ma5_points = []
        ma5_list = []
        for i in range(num_points):
            # this_end = last_end + 10
            # this_end = np.random.uniform(100,150)
            if file_name == 'aaaa1':
                this_end = pattern[i % len(pattern)] + np.random.uniform(-0.5,0.5)
            elif file_name == 'aaaa2':
                this_end = last_end + change_pattern[i % len(pattern)] + np.random.uniform(-0.5,0.5)
            end_points.append(this_end)
            ma5 = get_ma_n(end_points, 5)
            ma5_points.append(ma5)
            this_piece = [str(time_step), str(last_end), str(max(last_end,this_end)), str(min(last_end,this_end)), str(this_end), '0', '0', '0', '1']
            all_pieces.append(this_piece)
            last_end = this_end
            time_step += 1

        dumps = json.dumps(all_pieces)
        f.write(dumps)

    # freq = np.array(get_fft(end_points, 100))
    # plt.plot(freq, marker='o')
    # plt.show()

    ypoints = np.array(end_points)
    ma5 = np.array(ma5_points)

    plt.plot(ypoints, marker='')
    plt.plot(ma5, marker='')
    plt.show()

gen_data('aaaa1', 500)
gen_data('aaaa2', 500)
