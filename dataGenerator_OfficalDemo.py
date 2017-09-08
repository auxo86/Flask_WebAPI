# -*- coding: utf-8 -*-
#!~/flask/bin/python3

from flask import Flask, jsonify, g
from flask_cors import CORS, cross_origin
import sqlite3
import os


app = Flask(__name__)
CORS(app)


'''
本程式用於產生餵給D3.js GEO功能的JSON dict資料
讀取sqlite3，產生字典，然後轉成JSON
'''

# 設定語言環境
os.environ['NLS_LANG'] = 'TRADITIONAL CHINESE_TAIWAN.AL32UTF8'

numStartYr = 65
numDiffYr = 85
numDiagYr = 100
numEndYr = numStartYr + numDiffYr

# 要讀取的資料表名稱
str_tableNameForGet = "N_DIAGDATE_GEODATA"
# 讀取資料表的SQL字串
strSQLReadData = f'''select
  VILLAGE_ID
  , count(VILLAGE_ID) as population
from
  {str_tableNameForGet}
where
  (julianday('now') - julianday(BIRTHDATE))/365 > {numStartYr}
  and (julianday('now') - julianday(BIRTHDATE))/365 <= {numEndYr}
  and (julianday('now') - julianday(N_DIAGDATE))/365 <= {numDiagYr}
group by 
  VILLAGE_ID
order by
  population desc'''

# 準備要存入資料的字典
dictData = {}
# 設定資料庫位置
strDB = "ptDiagtimeGeodata.db"


# 要在flask中使用sqlite3，不是很直覺，要參考文擋
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(strDB)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/GISSYS/api/geopopdata', methods=['GET'])
@cross_origin()
def get_tasks():
    db = get_db()
    cur = db.execute(strSQLReadData)
    listAllRows = [row for row in cur]
    '''
    資料應該是長這樣[{
      "tasks": [
        [
          6301000029, 
          90768
        ], 
        [
          6301000039, 
          89266
        ], 
        [
          6300500002, 
          32507
        ], , ...]
    '''
    for rowitem in listAllRows:
        key = rowitem[0]
        value = rowitem[1]
        dictData[key] = value
    return jsonify({'tasks': dictData})


if __name__ == '__main__':
    app.run()

