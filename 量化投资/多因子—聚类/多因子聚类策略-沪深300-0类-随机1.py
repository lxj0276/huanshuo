import pandas as pd
import numpy as np
import datetime
from pandas.core.frame import DataFrame
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import random

def initialize(account):
    # 使用智能选股函数设置股票池 
    get_iwencai('沪深300')
    
    # 设置调仓周期，每月第二个交易日运行
    schedule_function(func=cluster, date_rule=date_rules.month_start(1))
    
#ss = random.randint(0,9999)

def cluster(account, data):
    '''if len(account.positions) > 0:
        # 止损：个股跌幅超过10%，卖出
        securities = list(account.positions)
        for stock in securities:
            price = data.attribute_history(stock, ['close'], 1, '1d', skip_paused=False, fq='pre')
            if account.positions[stock].cost_basis /price['close'][0]-1 < -0.1:
                order_target(stock, 0)'''
    for security in list(account.positions):
        order_target(security, 0)
    
    # 首先获得当前日期
    time = get_datetime()
    date = time.strftime('%Y%m%d')
    
    #log.info(ss)
    # 获得股票池列表
    sample = account.iwencai_securities
    # 创建字典用于存储因子值
    df = {'security':[], 1:[], 2:[], 3:[],'score':[]}
    
    # 因子选择
    for security in sample:
        q=query(
            profit.roic,# 投资回报率
            valuation.pe,# 市盈率
            valuation.ps_ttm,# 市销率
        ).filter(
            profit.symbol==security
        )
        
        # 缺失值填充为0
        fdmt = get_fundamentals(q, date=date).fillna(0)
        
        # 判断是否有数据
        if (not (fdmt['profit_roic'].empty or
                fdmt['valuation_pe'].empty or
                fdmt['valuation_ps_ttm'].empty)):
            # 计算并填充因子值
            df['security'].append(security)
            df[1].append(fdmt['profit_roic'][0])# 因子1：投资回报率
            df[2].append(fdmt['valuation_pe'][0])# 因子2：市盈率
            df[3].append(fdmt['valuation_ps_ttm'][0])#因子3：市销率
    
    for i in range(1, 4):
        #去除异常值
        m = np.mean(df[i])
        s = np.std(df[i])
        for j in range(len(df[i])):
            if df[i][j] <= m-3*s:
                df[i][j] = m-3*s
            if df[i][j] >= m+3*s:
                df[i][j] = m+3*s
        m = np.mean(df[i])
        s = np.std(df[i])
        
        # 因子标准化
        for j in range(len(df[i])):
            df[i][j] = (df[i][j]-m)/s
    
    for i in range(len(df['security'])):
        # 等权重计算
        s = (df[1][i]-df[2][i]-df[3][i])
        df['score'].append(s)
        
    # 按综合因子得分由大到小排序
    df = pd.DataFrame(df).sort_values(by ='score', ascending=False)
    df = df.reset_index(drop=True)
    df = df[0:100]
    log.info(df)
    
    data = df.loc[:,[1,2,3]]
    k = 10 #聚类的类别
    iteration = 300 #聚类最大循环次数
    data = data
    data_zs = 1.0*(data - data.mean())/data.std() #数据标准化
    model = KMeans(n_clusters = k, n_jobs = 4, max_iter = iteration,random_state = 1 ) #分为k类, 并发数4
    model.fit(data_zs) #开始聚类
    #简单打印结果
    r1 = pd.Series(model.labels_).value_counts() #统计各个类别的数目
    r2 = pd.DataFrame(model.cluster_centers_) #找出聚类中心
    r = pd.concat([r2, r1], axis = 1) #横向连接(0是纵向), 得到聚类中心对应的类别下的数目
    r.columns = list(data.columns) + [u'类别数目'] #重命名表头
    log.info(r)
    
    #详细输出原始数据及其类别
    r = pd.concat([data, pd.Series(model.labels_, index = data.index)], axis = 1)  #详细输出每个样本对应的类    
    r.columns = list(data.columns) + [u'聚类类别'] #重命名表头
    t= r.loc[:,'聚类类别']
    df.insert(4,'聚类类别',t)
    cc = df[(df.聚类类别 == 0)]
    cc = cc.reset_index(drop=True)
    ee = cc.loc[:,['security']]
    dd = ee['security'].values.tolist()
    log.info(dd)
    
    # 等权重分配资金
    cash = account.cash/len(dd)
    
    # 买入新调仓股票
    for security in dd:
        order_target_value(security, cash)
        
def handle_data(account,data):
    pass