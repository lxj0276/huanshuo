import tushare as ts
import pandas as pd
from pandas.core.frame import DataFrame

a = ts.get_hs300s()

qq = []
m = 1
for i in a.iloc[:,1]:
    s = ts.get_hist_data(i,start='2016-01-01',end='2017-01-01')
    print('正在保存第{0}个数据，代码是{1}'.format(m,i))
    try:
        n = str(i) + '.csv'
        s.to_csv(n)
        m += 1
        qq.append(i)
    except:
        print('第{0}个数据保存失败，代码是{1}'.format(m,i))
        m += 1
        pass


temp = pd.DataFrame(columns = ['date','ma5','volume','v_ma5','turnover','p_change']) #创建用于储存的空数据框
for file in qq:
    file = str(file)
    excel_path = '/Users/liuhuanshuo/Desktop/zuoye/lianghua/data/' + file + '.csv'
    df = pd.read_csv(excel_path) 
    df_one = df.loc[:,['date','ma5','volume','v_ma5','turnover','p_change']]  #切片 提取指定列
    a = df_one[(df_one.date == '2016-04-01')] #选择特定行
    temp = temp.append(a,ignore_index=True) #将刚刚选取的行添加到数据框中，可以帮助忽略index，自动递增
temp

data = temp.loc[:,['ma5','volume','v_ma5','turnover','p_change']]


import pandas as pd

#参数初始化


k = 5 #聚类的类别

iteration = 500 #聚类最大循环次数

data = data

data_zs = 1.0*(data - data.mean())/data.std() #数据标准化

from sklearn.cluster import KMeans

model = KMeans(n_clusters = k, n_jobs = 2, max_iter = iteration) #分为k类, 并发数4

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


from sklearn.manifold import TSNE
tsne = TSNE()
tsne.fit_transform(data_zs) #进行数据降维
tsne = pd.DataFrame(tsne.embedding_, index = data_zs.index) #转换数据格式
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False #用来正常显示负号
#不同类别用不同颜色和样式绘图
d = tsne[r[u'聚类类别'] == 0]
plt.plot(d[0], d[1], 'r.')
d = tsne[r[u'聚类类别'] == 1]
plt.plot(d[0], d[1], 'go')
d = tsne[r[u'聚类类别'] == 2]
plt.plot(d[0], d[1], 'b*')
d = tsne[r[u'聚类类别'] == 3]
plt.plot(d[0], d[1], 'g+')
d = tsne[r[u'聚类类别'] == 4]
plt.plot(d[0], d[1], 'y+')
'''d = tsne[r[u'聚类类别'] == 5]
plt.plot(d[0], d[1], 'b+')'''
plt.show()

