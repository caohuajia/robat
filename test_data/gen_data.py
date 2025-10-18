##  timestap         begin      highest    lowest     end                                      complete
## ['1729861200000', '0.14621', '0.14662', '0.14578', '0.14656', '33498', '334980', '48981.5551', '1']

import matplotlib.pyplot as plt
import numpy as np

pattern        = [100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 150, 150, 150, 150, 150, 150, 150, 150, 150, 150]
change_pattern = [ 3,  3,  3,  3,  3, -0.2, -0.2, -0.2, -0.2, -0.2,  3,  3,  3,  3,  3, -0.2, -0.2, -0.2, -0.2, -0.2]

def get_ma_n(lst, n):
    if len(lst) < n:
        return sum(lst)/len(lst)
    else:
        return sum(lst[-n:])/n

def gen_data(file_name, num_points):
    file_path = 'test_data/{}'.format(file_name)
    with open('test_data/z_data1.json', 'w') as f:
        time_step = 0
        last_end = 100
        end_points = []
        ma5_points = []
        ma5_list = []
        for i in range(100):
            # this_end = last_end + 10
            # this_end = np.random.uniform(100,150)
            if file_name == 'z_data1.json':
                this_end = pattern[i % len(pattern)] + np.random.uniform(-0.5,0.5)
            elif file_name == 'z_data2.json':
                this_end = last_end + change_pattern[i % len(pattern)] + np.random.uniform(-0.5,0.5)
            end_points.append(this_end)
            ma5 = get_ma_n(end_points, 5)
            ma5_points.append(ma5)
            this_piece = [str(time_step), str(last_end), str(max(last_end,this_end)), str(min(last_end,this_end)), str(this_end), '0', '0', '0', '1']
            last_end = this_end
            time_step += 1

            f.write(str(this_piece) + '\n')
    return end_points, ma5_points

# end_points, ma5_points = gen_data('z_data1.json', 100)
end_points, ma5_points = gen_data('z_data2.json', 50)

ypoints = np.array(end_points)
ma5 = np.array(ma5_points)

plt.plot(ypoints, marker='')
plt.plot(ma5, marker='')
plt.show()