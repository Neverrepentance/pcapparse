#!/usr/bin/python3
# coding=utf-8


from clickhouse_driver import Client


if __name__ == '__main__':
    client = Client(host='172.16.61.29',port='9000',database='dsa_audit_log',user='default',password='Secsmart#612')
    sql = 'select toStartOfFiveMinute(request_time),count(1) from sql_log group by toStartOfFiveMinute(request_time)'
    coll= client.execute(sql)
    copy_sql='insert into sql_log (first_id,second_id,asset_id,log_version,session_id,client_mac,client_ip,client_port,server_mac,server_ip,server_port,request_time,request_time_usec,execute_time,request_status,account,os_user_name,risk_type,matched_rules,risk_level,protect_operate,instance_name,client_app,client_host,operation_statement,binding_variables,statement_pattern,reply,error_reply,error_code,rows_affected,operation_type,operation_command,operand_type,operand_name,second_operand_name,web_user_name,web_url,web_ip,web_session_id)  select first_id,second_id,asset_id,log_version,session_id,client_mac,client_ip,client_port,server_mac,server_ip,server_port,timestamp_sub(MONTH, 1,request_time),request_time_usec,execute_time,request_status,account,os_user_name,risk_type,matched_rules,risk_level,protect_operate,instance_name,client_app,client_host,concat(operation_statement,''--  comment '',toString(number),binding_variables,statement_pattern,reply,error_reply,error_code,rows_affected,operation_type,operation_command,operand_type,operand_name,second_operand_name,web_user_name,web_url,web_ip,web_session_id from sql_log, numbers({}}) where toStartOfFiveMinute(request_time)={}'
    for dtime,num in coll:
        client.execute(copy_sql.format(num,dtime))