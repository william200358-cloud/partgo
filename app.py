from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

# 🛠️ 雲端自動點火：每次重開都強迫刷新，把大量越野車比價零件灌進去
def init_db_if_not_exists():
    if True:  # 強迫刷新資料
        print("正在為雲端注入真實越野車零件比價數據...")
        conn = sqlite3.connect('parts.db')
        cursor = conn.cursor()
        
        cursor.execute('DROP TABLE IF EXISTS parts')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                source TEXT NOT NULL,
                price INTEGER NOT NULL,
                link TEXT
            )
        ''')
        
        # 🎯 基於你的三個真實網址，衍生出的大量比價選項（包含地墊、避震、FB社團）
        dummy_parts = [
            # 1. Rough Country 地墊比價組（有便宜有貴，測試自動排序）
            ('Jeep Gladiator (2021) 專用全天候防水腳踏墊 (Rough Country 二手極新 / 腳踏墊專區)', '中部 4x4 改裝工坊', 2900, 'https://www.roughcountry.com/floor-mats-cargo-liners/jeep/gladiator/2021'),
            ('Jeep Gladiator (2021) 專用全天候防水腳踏墊 / 後行李箱襯墊 (Rough Country 原廠件)', '北部 4x4 零件交流商', 3200, 'https://www.roughcountry.com/floor-mats-cargo-liners/jeep/gladiator/2021'),
            ('Jeep Gladiator Rough Country 全天候防水地墊 (全新現貨代購)', '南部越野精品百貨', 4200, 'https://www.roughcountry.com/floor-mats-cargo-liners/jeep/gladiator/2021'),
            
            # 2. Lucky8 LLC 避震改裝比價組
            ('Land Rover Discovery / Defender 專用外匯升級避震套件 (Lucky8 專家推薦款)', 'Lucky8 LLC 台灣代購組', 26000, 'https://lucky8llc.com/'),
            ('Land Rover Defender 2020+ 專用外匯越野改裝精品避震器減震筒 (全新進口)', '高雄雙B越野殺肉廠', 28500, 'https://lucky8llc.com/'),
            ('Lucky8 原裝進口 Land Rover 全系列越野懸吊升級高階避震系統', '執著 4x4 改裝俱樂部', 31000, 'https://lucky8llc.com/'),
            
            # 3. FB 社團與車友交流組
            ('越野四驅車材料零件與全台報廢車殺肉件買賣交流社團 (車友交流/零件尋寶)', 'Facebook 越野車零件交流社團', 0, 'https://www.facebook.com/groups/325391057802702'),
            ('Jeep / Land Rover 報廢車殺肉件買賣與越野改裝二手零件交流專區', 'Facebook 越野車零件交流社團', 0, 'https://www.facebook.com/groups/325391057802702')
        ]
        
        cursor.executemany('INSERT INTO parts (name, source, price, link) VALUES (?, ?, ?, ?)', dummy_parts)
        conn.commit()
        conn.close()
        print("雲端真實比價數據初始化成功！")

init_db_if_not_exists()

# 🔍 前台搜尋：核心內建 ORDER BY price ASC（價格由低到高自動排序，0面議排最前）
@app.route('/')
def index():
    query = request.args.get('query', '')
    brand = request.args.get('brand', '')
    results = []
    
    if query:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if brand and brand != '選擇品牌':
            cursor.execute("SELECT * FROM parts WHERE name LIKE ? AND name LIKE ? ORDER BY price ASC", 
                           ('%' + query + '%', '%' + brand + '%'))
        else:
            cursor.execute("SELECT * FROM parts WHERE name LIKE ? ORDER BY price ASC", ('%' + query + '%',))
            
        results = cursor.fetchall()
        conn.close()
        
    return render_template('index.html', results=results, query=query, brand=brand)

# 🛠️ 後台管理：隨時手動無限制新增更多真實零件網址
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        source = request.form['source']
        price = request.form['price']
        link = request.form['link']
        
        cursor.execute('INSERT INTO parts (name, source, price, link) VALUES (?, ?, ?, ?)',
                       (name, source, price, link))
        conn.commit()
        return redirect(url_for('admin'))
        
    cursor.execute('SELECT * FROM parts ORDER BY id DESC')
    all_parts = cursor.fetchall()
    conn.close()
    return render_template('admin.html', all_parts=all_parts)

if __name__ == '__main__':
    app.run()