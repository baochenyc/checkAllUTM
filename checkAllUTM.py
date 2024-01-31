import requests
import json
import pymysql
import datetime

db_settings = {
    "host": "10.200.10.153",
    "port": 3306,
    "user": "userdbc",
    "password": "cBDrESu",
    "db": "chenyc",
    "charset": "utf8"
}

try:
    # 建立Connection物件
    dbConn = pymysql.connect(**db_settings)
except Exception as ex:
    print(ex)

cursor = dbConn.cursor()


session = requests.Session()


# login LCMS
api_url = "http://lcms.secom.com.tw:4221"
dataobj = {"data": {"id":"cmsadmin","password":"cmssecretpass"}}
headers =  {"Content-Type":"application/json"}
cmd_url=api_url+'/apis/v1/sign_in'
response = session.post(cmd_url, json=dataobj,headers=headers)


# get all utm
cmd_url=api_url+'/apis/v1/boxes'
response = session.get(cmd_url,headers=headers)
jData=response.json()


chkstr=datetime.datetime.now().strftime('%Y%m%d')

for dataobj in jData['data']:
    online="Y" if dataobj['online']==True else "N"
    lcm_updater="Y" if dataobj['lcm_updater']==True else "N"
    lcm_log_non_required="Y" if dataobj['lcm_log_non_required']==True else "N"




    command = "SELECT id FROM utmv2_boxes where id=%s"
    rc=cursor.execute(command, (dataobj['id'],))     
    if rc > 0:
        result = cursor.fetchone()
        command = "update utmv2_boxes set ip=%s, online=%s,updt=now(),chk=%s  where id=%s"
        rc=cursor.execute(command, ( dataobj['ip'],online,chkstr, dataobj['id'],))   
        # dbConn.commit()             
    else:    

        command = "INSERT INTO utmv2_boxes (id,model,proj_code,name,nick,ip,version,new_fw_ver,av_sig_ver,ips_sig_ver,wg_sig_ver,sig_updated_at,created_at,alerted_at,configured_at,upgrade_fw_at,subscription_expired_at,online,lcm_updater,lcm_log_non_required,ctdt,updt,chk) "
        command +="                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now(),%s)"

        cursor.execute(command, (dataobj['id'],dataobj['model'],dataobj['proj_code'],dataobj['name'],dataobj['nick'],
                                 dataobj['ip'],dataobj['version'],dataobj['new_fw_ver'],dataobj['av_sig_ver'],dataobj['ips_sig_ver'],
                                 dataobj['wg_sig_ver'],dataobj['sig_updated_at'],dataobj['created_at'],dataobj['alerted_at'],dataobj['configured_at'],
                                 dataobj['upgrade_fw_at'],dataobj['subscription_expired_at'],online,lcm_updater,lcm_log_non_required,chkstr
                                 ))  
        # dbConn.commit()
dbConn.commit()

cmd_url=api_url+'/apis/v1/groups'
response = session.get(cmd_url,headers=headers)
jData=response.json()

for dataobj in jData['data']:
    # online="Y" if dataobj['online']==True else "N"
    # lcm_updater="Y" if dataobj['lcm_updater']==True else "N"
    # lcm_log_non_required="Y" if dataobj['lcm_log_non_required']==True else "N"

    command = "SELECT id FROM utmv2_groups where id=%s"
    rc=cursor.execute(command, (dataobj['id'],))     
    if rc > 0:
        result = cursor.fetchone()
        command = "update utmv2_groups set chk=%s,updt=now()  where id=%s"
        rc=cursor.execute(command, ( chkstr, dataobj['id'],))   
        # dbConn.commit()             
    else:    

        for box in dataobj['bids']:

            command = "INSERT INTO utmv2_groups (id,name,configured_at,box,ctdt,updt,chk) "
            command +="                 VALUES (%s, %s, %s,%s, now(), now(),%s)"

            cursor.execute(command, (dataobj['id'],dataobj['name'],dataobj['configured_at'],box,chkstr
                                    ))  
            # dbConn.commit()
dbConn.commit()

