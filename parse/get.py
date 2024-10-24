#!/usr/bin/python3
# coding=utf-8
import matplotlib as mpl
mpl.use("agg")

import matplotlib.pyplot as plt 
import pandas as pd 
import json
import numpy as np 
from datetime import *
from clickhouse_driver import Client
from scipy.fftpack import fft, fftfreq
from scipy import stats
import scipy.signal as signal
from statsmodels.tsa.stattools import acf

class DB_Obj(object):
    def __init__(self, db_name) -> None:
        self.db_name = db_name
        host = '127.0.0.1'
        port = '9000'
        user = 'default'
        password = 'Secsmart#612'
        database = db_name
        send_recive_timeout = 150
        self.client = Client(host=host,port=port,database=database,user=user,password=password)

    def save_csv(self, df_trade, filename):
        df_trade.to_csv(filename,mode='w',encoding='utf-8',index=False)

    def get_data(self,sql, filename):
        n = 0
        k = 0
        batch = 100000
        i = 0
        flag = True
        while flag:
            self.sql = sql.format(n , n+batch)
            coll = self.client.query_dataframe(self.sql)
            df_trade = coll
            i = i+1
            k = len(df_trade)
            if k > 0 :
                self.save_csv(df_trade, filename)

            n = n + batch
            if k == 0 :
                flag = False

## 画时序图
def plot_df(x, y, filename, title='', xlabel='Date', ylabel='Value', dpi=100):
    plt.figure(figsize=(16,5),dpi=dpi)
    plt.plot(x,y,color='tab:red')
    plt.gca().set(title=title, xlabel=xlabel, ylabel=ylabel)
    plt.savefig(filename)
    plt.close()


## 使用傅里叶变换估计波形图的周期
def find_periods(data):
    series = fft(data)
    power = np.abs(series)
    sample_freq = fftfreq(series.size)

    mask = np.where(sample_freq > 0)
    freqs = sample_freq[mask]
    powers = power[mask]
    

    # plt.plot(1/freqs, powers)
    # plt.title('Frequency Spectrum')
    # plt.xlabel('Frequency (Hz)')
    # plt.ylabel('Amplitude')
    # plt.savefig('Frequency.png')
    # plt.close()

    top_k_seasons = 5
    top_k_idxs = np.argpartition(powers, -top_k_seasons)[-top_k_seasons:]
    # top_k_power = powers[top_k_idxs]
    periods = (1 / freqs[top_k_idxs]).astype(int)
    return periods

## 使用傅里叶变换估计波形图的周期
def find_periods3(data):
    ft = fft(data)
    freqs = fftfreq(len(data), 1)
    mags = np.abs(ft)

    inflection = np.diff(np.sign(np.diff(mags)))
    peaks = (inflection < 0).nonzero()[0] + 1
    peak = peaks[mags[peaks].argmax()]
    signal_peak = freqs[peak]
    period = list()
    period.append(int(1/signal_peak))
    return (period)


## 使用傅里叶变换估计波形图的周期
def find_periods2(data, n=5, fmin=0.2):
    yf = np.abs(fft(data))
    yfnormlize = yf / len(data)
    yfhalf = yfnormlize[range(int(len(data)/2))]
    yfhalf = yfhalf * 2
    
    fwbest = yfhalf[signal.argrelextrema(yfhalf, np.greater)]
    xwbest = signal.argrelextrema(yfhalf, np.greater)

    xorder = np.argsort(-fwbest)
    xworder = list()
    xworder.append(xwbest[x] for x in xorder)
    fworder = list()
    fworder.append(fwbest[x] for x in xorder)

    if len(fwbest) <=n:
        return (len(data)/xwbest[0][:len(fwbest)]).astype(int)
    else:
        return (len(data)/xwbest[0][:n]).astype(int)

## 计算周期的相似性（计算各个周期的相关系数）
def expect_period(data, periods):
    # 最大相似性
    max_score = 0
    # 最大相似性时的周期
    max_score_period = 0


    ## 计算输入的周期
    for lag in periods:
        score = acf(data, nlags=lag, fft=False)[-1]
        if score > max_score:
            max_score = score
            max_score_period = lag

    ## 计算常见周期: 半天，1天，1周，1月
    except_lag = np.array([timedelta(hours=12)/timedelta(minutes=5),    \
                        timedelta(days=1)/timedelta(minutes=5),     \
                        timedelta(days=7)/timedelta(minutes=5),     \
                        timedelta(days=30)/timedelta(minutes=5)]).astype(int)
    for lag in except_lag:
        score = acf(data, nlags=lag, fft=False)[-1]
        if score > max_score:
            max_score = score
            max_score_period = lag

    
    # autocorrelation = pd.Series(data).autocorr(lag=max_score_period)
    # pd.plotting.autocorrelation_plot(data)
    # plt.savefig('expect.png')
    # plt.close()

    return max_score_period, max_score


# 判断是否正态分布
def check_stats(data):
    u = data.mean()
    std = data.std()
    p = stats.kstest(data,'norm',(u, std))
    return p.pvalue > 0.05

## 按照标准差查找异常值，正态分布时，1个标准差68%，2个标准差95%， 3个标准差 99.7%
def zscore_data(data,key, threshold = 2):
    score = (data[key] - data[key].mean())/np.std(data[key])
    outliers = np.where(score > threshold)[0]
    return data[outliers]

if __name__ == '__main__':
    db_obj = DB_Obj('secsmart_audit_log')
    db_obj.get_data('select client_ip, count(1) as times from sql_log where operation_type=1 group by client_ip order by times desc limit {},{}','all.csv')

    ip_info = pd.read_csv('all.csv')
    for i in range(len(ip_info)):
        times = int(ip_info['times'][i])
        if times < 5:  #  访问次数太低没有周期
            continue
        ip = ip_info['client_ip'][i]
        db_obj.get_data('select toStartOfFiveMinute(request_time) as start_time, count(1) as times from sql_log where operation_type = 1 and client_ip = \''+ip+'\' group by start_time limit {},{}', 'login.csv')

        df = pd.read_csv('login.csv')
        ## 缺失项填充
        df['start_time']=pd.to_datetime(df['start_time'], format='%Y-%m-%d %H:%M:%S')
        helper = pd.DataFrame({'start_time':pd.date_range(df['start_time'].min(), df['start_time'].max(), freq='300s')})
        ret = pd.merge(df, helper, on='start_time', how='outer').sort_values('start_time')
        ret.fillna(0, inplace=True)
        ret = ret.reset_index(drop=True)


        ## 计算周期
        np.seterr(invalid='ignore')
        periods = find_periods(ret['times'].values)
        period,score = expect_period(ret['times'].values, periods)
        if score > 0.8 :
            print(f"IP {ip} 的登录行为存在周期规律，最匹配的周期:{period}, 相关性:{score}")            
            # 画时序图
            plot_df(ret.start_time, ret.times, ip+'login.png','login times per 5m in secsmart audit log', 'start time', "times")


            ret['group']=(ret.index // period) + 1
            group_ip = ret.groupby('group')['times'].sum()
            group_ip= group_ip.rename('times').reset_index()

            is_stat= check_stats(group_ip['times'].values)
            if is_stat :
                print(f'IP {ip}的登录事件在周期{period}个5分钟内, 登录次数符合正态分布')
                group_ip['times'].plot.kde()
                plt.savefig(ip+'_stat.png')
                plt.close()
            
            abnormal = zscore_data(group_ip,'times')
            if abnormal.size > 0:
                print(f'IP {ip}的登录次数超过2个标准差的周期: ')
                print(abnormal)
            else:
                print(f'IP {ip}的登录次数没有异常周期(超过2个标准差)')

        # else:
        #     print(f"无周期特征，最匹配的周期:{period}, 相似度:{score}")
