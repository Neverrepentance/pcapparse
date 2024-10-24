import pymysql
import re
import time

# connlist=[]
# for i in range(30):
#     conn=pymysql.connect(
#         host="172.16.37.95",
#         port=3306,
#         user='root',
#         password='1',
#         database='jjjtest',
#         charset='utf8')
#     connlist.append(conn)

errorCount = 0
sqlCount = 0

def excuetesql(conn,sql):
    global errorCount,sqlCount
    cue=conn.cursor()
    try:
        cue.execute(sql)
        for row in cue:
            print(row)
    except Exception as e:
        errorCount = errorCount +1
        
    sqlCount = sqlCount +1

def read():
    global sqlCount,connlist
    fileName="./longsql.txt"
    maxsize = 0
    with open(fileName,'r') as f:
        lines=f.readlines()
        # while True:
        conn=pymysql.connect(
            host="172.16.37.95",
            port=3306,
            user='root',
            password='1',
            database='jjjtest',
            charset='utf8')
        for line in lines:
            excuetesql(conn,line + "# idx:"+ str(sqlCount))
            time.sleep(1)
        conn.close()

read()
print("excute sql :%d , error: %d, success: %d"%(sqlCount, errorCount, sqlCount - errorCount))