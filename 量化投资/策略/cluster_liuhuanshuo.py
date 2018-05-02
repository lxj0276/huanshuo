
# coding: utf-8

# In[94]:


'''
    多因子选股：聚类+择时+轮动
    给出需要执行策略的时间区间以及本金，就可以自动对沪深300股票池进行kmeans聚类并且对表现较好的一类进行轮动轮动
    
    IDE: Jupyter Notebook  
    python version: python3.6
    platform: macOS High Sierra 10.13.4
    liuhuanshuo: huanshuo0801@Gmail.com
    Apr,27,2018
'''


# In[95]:


from sklearn.cluster import KMeans
import pandas as pd
import time
import os
from pandas.core.frame import DataFrame
import tushare as ts
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


# In[96]:


def riqi(begin,end):
    '''
    将输入的开始和结束时间经过筛选给出需要进行轮动的时间区间
    时间已经人工处理过，在原始文件后分别添加三列buy end select记录当天状态
    '''
    print('--------正在计算时间区间---------')
    a = pd.read_excel('/Users/liuhuanshuo/Desktop/pool_date_new.xlsx') #读取经过处理的时间文件 
    k = 0
    for i in range(327): 
        '转换时间格式'
        a.ix[k,0] = a.ix[k,0].strftime("%Y-%m-%d")
        k = k+1
    
    s = list(a['日期']).index(begin) #提取开始时间的索引
    p = list(a['日期']).index(end)   #提取结束时间的索引
    a.ix[s,2] = 'F' #修改第一天的end为FALSE 这天不卖出
    a.ix[p,3] = 'F' #修改最后一天的select为FALSE 这天不计算
    t = a[s:p+1].reset_index(drop=True) #计算begin和end之间的交易日
    t = t.fillna(0)  #对空值填充0 方便之后处理
    return t


# In[97]:


def cluster(jisuanriqi):
    '''用于计算轮动时间内每最后一个交易日的聚类出的股票
       接受一个参数
       聚类的类别为9，最大迭代次数设置为500.并发数9！ 可以设置自定义！
       jisuanriqi为需要计算的整个时间区间
     '''
    print('--------正在聚类---------')
    b = ts.get_hs300s()
    vv = []
    dd = pd.DataFrame(columns = ['code','date','open','close'])
    for o in jisuanriqi['日期']:
        daima = pd.DataFrame(columns = ['code','open','close','ma5','ma10','v_ma10','turnover','volume','p_change'])
        for i in b['code']:
            try:
                s = ts.get_hist_data(i,start=o,end=o)
                s.insert(0,'code',i)
                s = s.loc[:,['code','open','close','ma5','ma10','v_ma10','turnover','volume','p_change']]
                daima = daima.append(s,ignore_index=True)
            except:
                pass
        daima.insert(1,'date',o)
        data = daima.loc[:,['ma5','ma10','v_ma10','turnover','volume','p_change']]
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
        print(r)

        #详细输出原始数据及其类别
        r = pd.concat([data, pd.Series(model.labels_, index = data.index)], axis = 1)  #详细输出每个样本对应的类别
        r.columns = list(data.columns) + [u'聚类类别'] #重命名表头
        r



        tsne = TSNE()
        tsne.fit_transform(data_zs) #进行数据降维
        tsne = pd.DataFrame(tsne.embedding_, index = data_zs.index) #转换数据格式
        plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
        #不同类别用不同颜色和样式绘图
        d = tsne[r[u'聚类类别'] == 0]
        plt.plot(d[0], d[1], 'r.')
        d = tsne[r[u'聚类类别'] == 1]
        plt.plot(d[0], d[1], 'bo')
        d = tsne[r[u'聚类类别'] == 2]
        plt.plot(d[0], d[1], 'b*')
        d = tsne[r[u'聚类类别'] == 3]
        plt.plot(d[0], d[1], 'g+')
        d = tsne[r[u'聚类类别'] == 4]
        plt.plot(d[0], d[1], 'y+')
        d = tsne[r[u'聚类类别'] == 5]
        plt.plot(d[0], d[1], 'b+')
        d = tsne[r[u'聚类类别'] == 6]
        plt.plot(d[0], d[1], 'b^')
        d = tsne[r[u'聚类类别'] == 7]
        plt.plot(d[0], d[1], 'r^')
        d = tsne[r[u'聚类类别'] == 8]
        plt.plot(d[0], d[1], 'g^')
        plt.show()

        t= r.loc[:,'聚类类别']
        daima.insert(10,'聚类类别',t)
        cc = daima[(daima.聚类类别 == 7)]
        cc = cc.reset_index(drop=True)
        ee = cc.loc[:,['code','date','open','close']]
        dd = dd.append(ee,ignore_index=True)
        xx = len(ee)
        vv.append(xx)
    
    temp = dd
    return temp,vv


# In[98]:


def mairuriqi(goumaidaima,t,vv):
    '''
    用于计算整个轮动期间的购买日的股票信息
    goumaidaima为之前的到的所有要购买的代码
    '''
    print('--------正在计算所有买入日期---------')
    mairuriqi = t[t['buy'] == 'T']  #选出买入日期
    mairude = [] #空列表存放每个日期的股票长度
    y = 0
    k = 0
    temp3 = pd.DataFrame(columns = ['code','date','open','close']) #创建空数据框存放数据
    for i in mairuriqi['日期']:
        temp5 = pd.DataFrame(columns = ['code','date','open','close'])
        for file in goumaidaima[y:vv[k]].code:
            excel_path = os.path.join('/Users','liuhuanshuo','desktop','zuoye','lianghua','策略/') + file + '.csv'
            df = pd.read_csv(excel_path) 
            df_one = df.loc[:,['code','date','open','close']]    #提取指定列
            a = df_one[(df_one.date == i)]  #选择出该日期的那一行
            temp3 = temp3.append(a,ignore_index=True)
            temp5 = temp5.append(a,ignore_index=True)
        w = len(temp5)
        mairude.append(w)
        y = y + k
        k = k + 1
    print(temp3)
    return temp3,mairude


# In[99]:


def maichudaima(goumaidaima,t,vv):
    '''
    用于计算整个轮动期间需要进行卖出股票的时间信息
    '''
    print('--------正在计算所有卖出日期---------')
    mairuriqi = t[t['end'] == 'T'] 
    maichude = []
    y = 0
    k = 0
    temp2 = pd.DataFrame(columns = ['code','date','open','close'])
    for i in mairuriqi['日期']:
        temp5 = pd.DataFrame(columns = ['code','date','open','close'])
        for file in goumaidaima[y:vv[k]].code:
            excel_path = os.path.join('/Users','liuhuanshuo','desktop','zuoye','lianghua','策略/') + file + '.csv'
            df = pd.read_csv(excel_path) 
            df_one = df.loc[:,['code','date','open','close']]    #提取指定列
            a = df_one[(df_one.date == i)]  #选择特定行
            temp2 = temp2.append(a,ignore_index=True)
            temp5 = temp5.append(a,ignore_index=True)
        w = len(temp5)
        maichude.append(w)
        y = y + k
        k = k + 1
    print(temp2)
    return temp2,maichude


# In[100]:


def zhengchang(goumaidaima,t,vv):
    '''
    用于计算整个轮动期间的无需进行操作股票的时间信息
    '''
    print('--------正在计算所有无操作日期---------')
    zhengchang = t[t['buy'] == 0]
    zhengchang = zhengchang.reset_index(drop=True)
    maichu = t[t['end'] == 'T']
    maichu = maichu.reset_index(drop=True)
    zhengchangde = []
    y = 0
    k = 0
    temp4 = pd.DataFrame(columns = ['code','date','open','close'])
    for i in zhengchang['日期']:
        temp5 = pd.DataFrame(columns = ['code','date','open','close'])
        for j in maichu['日期'][k]:
            if i < j:
                for file in goumaidaima[y:vv[k]].code:
                    excel_path = os.path.join('/Users','liuhuanshuo','desktop','zuoye','lianghua','策略/') + file + '.csv'
                    df = pd.read_csv(excel_path) 
                    df_one = df.loc[:,['code','date','open','close']]    #提取指定列
                    a = df_one[(df_one.date == i)]  #选择特定行
                    temp4 = temp4.append(a,ignore_index=True)
                    temp5 = temp5.append(a,ignore_index=True)
                w = len(temp5)
                zhengchangde.append(w)
                y = y + k
                break
    print(temp4)
    return temp4,zhengchangde


# In[101]:


def lundong(t,temp2,temp3,temp4,mairude,maichude,zhengchangde):
    '''
    轮动
    接受八个参数：所有交易日期，购买日期，卖出日期，无操作日期以及后面三个日期中的每个股票的长度
    在购买日期 将可用资金平均分给每个股票 以开盘价格买入
    在卖出日期 以收盘价卖出全部股票
    在无操作日期 只需根据当天收盘价更新股票价值
    
    '''
    
    keyongzijin = cash #可用资金为cash
    chigujiazhi = 0 #初始持股价值为0
    keyongzijin_1 = [] #空列表用于每次更新可用价值，下同
    chigujiazhi_1 = []
    chigushuliang = []  #创建空列表存储持股数量
    pp = 0
    kk = 0
    gg = 0
    tt = 0  #mairude里面的
    cc = 0  #maichude里面的
    zz = 0  #zhengchangde里面的
    print('--------正在轮动中，初始资金为：{0}---------'.format(keyongzijin))
    for i in range(len(t)):

        if (t.ix[i,1] == 'T' and t.ix[i,2] == 'F'):
            print('第{0}个交易日买入'.format(i))
            goumaizijin = keyongzijin/mairude[tt] #购买每只股票的资金，平均分配

            for l in range(mairude[tt]):
                chigushuliang_1 = (goumaizijin/temp3.ix[l+pp,2])
                chigushuliang.append(chigushuliang_1)

            keyongzijin = 0 #第一次卖完变成0
            chigujiazhi = goumaizijin * mairude[tt]
            pp = pp + mairude[tt]
            tt = tt + 1
            keyongzijin_1.append(keyongzijin) #将本次结果添加进储存列表
            chigujiazhi_1.append(chigujiazhi)

        elif (t.ix[i,1] == 'F' and t.ix[i,2] == 'T'):
            print('第{0}个交易日卖出'.format(i))
            chigujiazhi = 0
            chucunzijin = []
            for y in range(maichude[cc]):
                keyongzijin_2 = chigushuliang[y] * temp2.ix[y+kk,3]
                chucunzijin.append(keyongzijin_2)
            kk = kk + maichude[cc]
            cc = cc + 1
            keyongzijin = sum(chucunzijin)
            keyongzijin_1.append(keyongzijin)
            chigujiazhi_1.append(chigujiazhi)

        elif (t.ix[i,1] == 0 and t.ix[i,2] == 0 and t.ix[i,3] == 0):
            print('第{0}个交易日，无操作'.format(i))
            xianyoujiazhi = []
            for z in range(zhengchangde[zz]):
                xianyoujiazhi_1 = chigushuliang[z] * temp4.ix[z + gg,3]
                xianyoujiazhi.append(xianyoujiazhi_1)
            gg = gg + zhengchangde[zz]
            chigujiazhi = sum(xianyoujiazhi)
            keyongzijin_1.append(keyongzijin)
            chigujiazhi_1.append(chigujiazhi)
        '''else:
            print('ok')
            keyongzijin_1.append(keyongzijin)
            chigujiazhi_1.append(chigujiazhi)'''

    c={"可用资金" : keyongzijin_1,
       "持股价值" : chigujiazhi_1}
    data1=DataFrame(c)
    data1.insert(0,'日期',t['日期'])
    data1['总资产'] = data1['可用资金'] + data1['持股价值'] #计算总资产
    data1 = data1.drop(len(data1)-1)
    
    return data1


# In[102]:


def huitu(data):
    '''
    接受最终结果，并绘图
    '''
    import matplotlib.pyplot as plt 
    import matplotlib.font_manager as fm
    myfont = fm.FontProperties(fname = '/Library/Fonts/Arial Unicode.ttf') #设置中文字体 https://www.zhihu.com/question/25404709/answer/67672003
    get_ipython().run_line_magic('matplotlib', 'inline')
    x = data.loc[:,['日期']]
    y = data.loc[:,['总资产']]
    plt.style.use('ggplot') #使用ggplot风格
    plt.plot(x,y)
    plt.xlabel('时间',fontproperties = myfont)
    plt.ylabel('资产',fontproperties = myfont)
    plt.title('策略图',fontproperties = myfont)


# In[103]:


def jisuan(begin,end):
    
    t = riqi(begin,end) #获得日期
    print(t)
    jisuanriqi = t[t['select'] == 'T'] #选择计算日期
    jisuanriqi = jisuanriqi.reset_index(drop=True)
    (goumaidaima,vv) = cluster(jisuanriqi)
    (temp3,mairude) = mairuriqi(goumaidaima,t,vv)
    (temp2,maichude) = maichudaima(goumaidaima,t,vv)
    (temp4,zhengchangde) = zhengchang(goumaidaima,t,vv)
    
    data = lundong(t,temp2,temp3,temp4,mairude,maichude,zhengchangde)
    huitu(data)
    return data


# In[104]:


begin ='2016-04-01'
end = '2016-04-15'
cash = 10000000
result = jisuan(begin,end)


# In[11]:


begin ='2016-04-01'
end = '2016-04-15'
cash = 10000000
result = jisuan(begin,end)


# In[29]:


begin =input('请输入策略开始时间：')
end = input('请输入策略结束时间：')
cash = input('请输入策略本金：')
cash = int(cash)
result = jisuan(begin,end)


# In[64]:


begin ='2016-04-01'
end = '2016-05-27'
cash = 10000000
result = jisuan(begin,end)

