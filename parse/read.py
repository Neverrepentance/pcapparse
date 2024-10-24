import pymysql
import re
import time

conn=pymysql.connect(
    host="172.16.37.95",
    port=3306,
    user='root',
    password='1',
    database='jjjtest',
    charset='utf8'
)

def excuetesql(sql):
    cue=conn.cursor()
    try:
        cue.execute(sql)
        for row in cue:
            print(row)
    except Exception as e:
        print("select error:",e)

def read():
    fileName="./sql_7.11.csv"
    maxsize = 0
    with open(fileName,'r') as f:
        while True:
            line=f.readline()
            if len(line) == 0 :
                break;
            
            if len(line) < 30*5000:
               continue
            else: 
                excuetesql('select * from t')
                time.sleep(1)
                excuetesql(line)
                time.sleep(1)

read()