def select_stock(riqi,shuliang):
    import pandas as pd
    import os
    print('你正在计算{0}的前{1}只股票的市盈率排序'.format(riqi,shuliang))
    df_list = pd.read_excel('/Users/liuhuanshuo/Desktop/作业/量化/stocks_list.xlsx')
    temp = pd.DataFrame(columns = ['代码','日期','市盈率'])
    for file in df_list['股票代码']:
        excel_path = os.path.join('/Users','liuhuanshuo','desktop','作业','量化','单佳雷数据','沪A股票原始数据/') + file + '.xls'
        df = pd.read_excel(excel_path)
        df_one = df.loc[:,['代码','日期','市盈率']]
        a = df_one[(df_one.日期 == riqi) & (df_one.市盈率 > 0)]
        temp = temp.append(a,ignore_index=True)  

    temp_sort = temp.sort_values(by = '市盈率')
    s = temp_sort.iloc[0:shuliang]
    s = s.reset_index(drop=True)
    return s
def stock_calculation():
    import pandas as pd
    import os
    df_date = pd.read_excel('/Users/liuhuanshuo/Desktop/作业/量化/20160401至20160601的日期.xlsx') #读取时间
    b = pd.DataFrame(columns = ['代码','日期','收盘价(元)']) #创建一个空数据框
    m = [] #创建一个list储存买入价格
    df_alldaysprofit = pd.DataFrame(columns = ['日期','代码','买入日期','买入价','收盘价(元)']) #创建一个空数据框
    for file in s['代码']:
        excel_path = os.path.join('/Users','liuhuanshuo','desktop','作业','量化','单佳雷数据','沪A股票原始数据/') + file + '.xls'
        df_oneof50 = pd.read_excel(excel_path)
        k = df_oneof50[df_oneof50.日期 == '2016/4/1'] #提取4月1日列
        g = k.iloc[0,4] #提取买入价格
        for i in df_date.日期:
            i = i.strftime('%Y/%m/%d') #用pandas自带数据包处理时间 https://blog.csdn.net/ly_ysys629/article/details/73822716
            t = df_oneof50[df_oneof50['日期'] == i] #提取列
            b = b.append(t,ignore_index=True) #向后添加进b
            b = b[['日期','代码','收盘价(元)']] #修改列名
            b.insert(2,'买入日期','2016-04-01') #插入添加买入时间列
            m.append(g) #添加买入价格
            b.insert(3,'买入价',m) #插入买入时间
    df_alldaysprofit = df_alldaysprofit.append(b) #将b添加到最后的数据框中
    q = (df_alldaysprofit.iloc[:,4] - df_alldaysprofit.iloc[:,3]) * 100 #计算当日盈亏
    df_alldaysprofit.insert(5,'该股票当日盈亏',q) #将当日盈亏插入
    return(df_alldaysprofit)
def calculating_profit():
    import pandas as pd
    import os
    date = pd.read_excel('/Users/liuhuanshuo/Desktop/作业/量化/20160401至20160601的日期.xlsx') #创建一个一列的数据框保存时间
    date.insert(1,'当日持仓股票个数',50) #在第一列插入当前持仓个数
    j = [] #创建一个空列表用于储存当日组合盈亏
    v = 0
    for h in date.日期:
        h = h.strftime('%Y/%m/%d')
        l = df_alldaysprofit[df_alldaysprofit['日期'] == h]
        n = l.iloc[:,5].sum()
        v += n
        j.append(v)
    date.insert(2,'当日组合盈亏',j) # 在第2列插入当日组合盈亏
    j = [] #创建一个空列表用于储存当日组合累计收益
    v = 0 
    for f in date.当日组合盈亏:
        v += f
        j.append(v)
    date.insert(3,'当日组合累计收益',j) # 在第3列插入当日组合盈亏
    return(date)
def plot():
    import pandas as pd
    import os
    import matplotlib.pyplot as plt 
    import matplotlib.font_manager as fm
    myfont = fm.FontProperties(fname = '/Library/Fonts/Arial Unicode.ttf') #设置中文字体 https://www.zhihu.com/question/25404709/answer/67672003
    x = date.loc[:,['当日组合盈亏']]
    y = date.loc[:,['当日组合累计收益']]
    plt.style.use('ggplot') #使用ggplot风格
    line_up, = plt.plot(x, label=u'当日组合盈亏')
    line_down, = plt.plot(y, label=u'当日组合累计收益')
    plt.legend(handles=[line_up, line_down],prop = myfont) #设置图例
    plt.xlabel('股票个数',fontproperties = myfont)
    plt.ylabel('收益',fontproperties = myfont)
    plt.title('50只股票收益组合策略收益图',fontproperties = myfont)