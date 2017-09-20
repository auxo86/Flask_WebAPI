# -*- coding: utf-8 -*-
# !~/flask/bin/python3

from flask import Flask, jsonify, render_template
from flask_cors import CORS, cross_origin
import sqlite3
import os
import json

app = Flask(__name__)
CORS(app)

'''
本程式用於產生餵給D3.js GEO功能的JSON dict資料
讀取sqlite3，產生字典，然後轉成JSON
'''

# 設定語言環境
os.environ['NLS_LANG'] = 'TRADITIONAL CHINESE_TAIWAN.AL32UTF8'
# 要讀取的資料表名稱
str_tableNameForGet = "N_DIAGDATE_GEODATA"
# 要寫入的路徑名稱
FileOutputDir = "TeipeiD3jsDynamicWithZoom/"
# 設定錯誤寫入的log檔案
fileErrLogName = str_tableNameForGet + "_JSON_Err.log"
# 設定使用的sqlite3資料連線
str_connect = "ptDiagtimeGeodata.db"


def fnGetDBConn(str_connect):
    conn = sqlite3.connect(str_connect)
    return conn


# 資料應該是長這樣[("6300100002", 133), ("6300100003", 329), ("6300100004", 371), ...]
def fnTupleToDict(tupleData):
    _dictData = {}
    for item in tupleData:
        key = item[0]
        value = (item[1], item[2])
        _dictData[key] = value
    return _dictData


def fnCloseResource(fileErrLog, cur, conn):
    fileErrLog.close()
    del cur
    conn.commit()
    conn.close()
    del conn


@app.route('/')
def index():
    return render_template('d3demo.html')


@app.route('/GISSYS/api/geopopdata/<int:numStartYr>/<int:numDiffYr>/<int:numDiagYr>', methods=['GET'])
@cross_origin()
def get_tasks(numStartYr, numDiffYr, numDiagYr):
    # 設定之後要轉成JSON的字典
    dictData = {}
    # 要寫入的檔案名稱
    strOutputJSONName = f"TPE_{numStartYr}_{numStartYr + numDiffYr}_in_{numDiagYr}Yr.json"
    # 讀取資料表的SQL字串
    strSQLReadData = f'''select a.n_village_id as village_id, count(a.n_village_id) as population, a.n_pop as all_pop from 
                        (
                      	    select
                      	      distinct pid as n_pid
                      	      , VILLAGE_ID as n_village_id
                      	      , pop as n_pop
                      	    from
                      	      N_DIAGDATE_GEODATA_TPE_NTPE
                      	    where
                      	      (julianday('now') - julianday(BIRTHDATE))/365 > {numStartYr}
                      	      and (julianday('now') - julianday(BIRTHDATE))/365 <= {numStartYr + numDiffYr}
                      	      and (julianday('now') - julianday(N_DIAGDATE))/365 <= {numDiagYr}
                        ) a
                      group by 
                        a.n_village_id, a.n_pop
                      order by
                        population desc'''

    if not os.path.exists(FileOutputDir):
        os.makedirs(FileOutputDir)
    # 開啟要寫入的json
    fileOutputJson = open(FileOutputDir + strOutputJSONName, 'w', encoding='utf-8')
    # 開啟要寫入的errlog
    fileErrLog = open(FileOutputDir + fileErrLogName, "w", encoding="utf-8")

    # 連接sqlite3資料庫
    conn = fnGetDBConn(str_connect)
    cur = conn.cursor()
    # 讀取資料，把資料存進List of tuple中
    cur.execute(strSQLReadData)
    tupleData = cur.fetchall()
    # 轉換tuple成為dict
    dictData = fnTupleToDict(tupleData)
    # 輸出檔案成json
    json.dump(dictData, fileOutputJson)
    # 關閉資源
    fnCloseResource(fileErrLog, cur, conn)

    return jsonify({'tasks': dictData})


if __name__ == '__main__':
    app.run(host='10.160.16.16', port=9999)
