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

def insert(id,txt1,txt2):
    cue=conn.cursor()
    try:
        cue.execute("insert into test(longtest,text2,test1) values(%s,%s,%s)",
                    [id,txt1,txt2])
    except Exception as e:
        print("insert error:",e)
        conn.rollback()
    else:
        conn.commit()


def select(id,txt1,txt2):
    cue=conn.cursor()
    try:
        cue.execute("select * from test;")
        for row in cue:
            print(row)
    except Exception as e:
        print("select error:",e)
    
def truncate(id,txt1,txt2):
    cue=conn.cursor()
    try:
        cue.execute("truncate table test;")
    except Exception as e:
        print("truncate error:",e)
        conn.rollback()
    else:
        conn.commit()
        

def read():
    filename="/root/data.txt"
    with open(filename,'r',encoding='UTF-8') as f:
        datas= f.readlines()
    
    for line in datas:
        text = re.split(r'\t|\n',line)
        insert(text[0],text[1],text[2])

read()
time.sleep(2)
select()
time.sleep(2)
truncate()
conn.close()