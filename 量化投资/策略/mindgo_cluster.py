
import matplotlib
matplotlib.use('Agg')
import tushare as ts
import pandas as pd
from pandas.core.frame import DataFrame
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import datetime

def initialize(account):  
    account.day = 10 #设置持有天数
    account.count = 0   #统计天数
    

def cluster():
    time = get_datetime()
    date = time.strftime('%Y-%m-%d')
    log.info(date)
    a = ts.get_hs300s()
    log.info(a)
    daima = pd.DataFrame(columns = ['code','open','close','ma5','ma10','v_ma10','turnover','volume','p_change'])
    for i in a['code']:
        try:
            s = ts.get_hist_data(i,start=date,end=date)
            s.insert(0,'code',i)
            s = s.loc[:,['code','open','close','ma5','ma10','v_ma10','turnover','volume','p_change']]
            daima = daima.append(s,ignore_index=True)
        except:
            pass
    data = daima.loc[:,['ma5','ma10','v_ma10','turnover','volume','p_change']]
    log.info(data)
    k = 9 #聚类的类别
    iteration = 500 #聚类最大循环次数
    data = data
    data_zs = 1.0*(data - data.mean())/data.std() #数据标准化
    model = KMeans(n_clusters = k, n_jobs = 9, max_iter = iteration) #分为k类, 并发数9
    model.fit(data_zs) #开始聚类
    #简单打印结果
    r1 = pd.Series(model.labels_).value_counts() #统计各个类别的数目
    r2 = pd.DataFrame(model.cluster_centers_) #找出聚类中心
    r = pd.concat([r2, r1], axis = 1) #横向连接(0是纵向), 得到聚类中心对应的类别下的数目
    r.columns = list(data.columns) + [u'类别数目'] #重命名表头
    log.info(r)
    
    #详细输出原始数据及其类别
    r = pd.concat([data, pd.Series(model.labels_, index = data.index)], axis = 1)  #详细输出每个样本对应的类别
    r.columns = list(data.columns) + [u'聚类类别'] #重命名表头
    t= r.loc[:,'聚类类别']
    daima.insert(9,'聚类类别',t)
    cc = daima[(daima.聚类类别 == 7)]
    cc = cc.reset_index(drop=True)
    ee = cc.loc[:,['code']]
    dd = ee['code'].values.tolist()
    gg = []
    for j in dd:
        if j[0]  == '6':
            j = j + '.SH'
            gg.append(j)
        else:
            j = j + '.SZ'
            gg.append(j)
        
    log.info(gg)
    return gg
    
def handle_data(account,data):
    if account.count == 0:
        if len(list(account.positions)) > 0:
            for s in list(account.positions):
                order(s,-100)
                log.info('卖出' + s)
        buy = cluster()
        for k in buy:
            order(k,100)
            log.info('买入' + k)
        account.count += 1
            
            
    elif account.count < account.day:
        account.count += 1
        log.info('持有' + str(account.count) + '天')
                    
    else:
        if account.count == account.day:
                account.count=0