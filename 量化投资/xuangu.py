def xuangu(riqi,shuliang):
    import pandas as pd
    import os
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