# robat
使用方法：
1. 下载数据： python3 download.py
2. 回测数据： python3 back_test.py  
        策略在  test_coin_class.py
        log在  log/test.log

3. balance 指的是现金， float 指的是当前总资产， total 指的是成交后的确认资产，未成交按买入价格算
4. 2 倍杠杆下：
        ma30 风险高，收益高，极端场景和ma60两极分化，ma30更多爆仓，收益为负，ma60收益为正
        较稳定货币：burst 和 gain正收益区间，ma30收益大部分比ma60高，负收益区间，各占一半
        大单边货币：ma30无论哪个区间劣势明显，甚至和ma60 两极分化
        下行周期，burst 0.5 0.6 0.7， gain稍比burst 小
        波动周期，burst 0.4， gain 0.5 左右