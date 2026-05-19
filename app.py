from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

# 🛠️ 雲端自動點火：強迫重刷成越野車資料庫
def init_db_if_not_exists():
    if True:  # 強迫刷新
        print("偵測到雲端未建立資料庫，正在自動初始化...")
        conn = sqlite3.connect('parts.db')
        cursor = conn.cursor()
        
        # 先確保表格乾淨（如果已有舊表先刪除，避免欄位或資料衝突）
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
        
dummy_parts = [
            ('Jeep Gladiator (2021) 專用全天候防水腳踏墊 / 後行李箱襯墊 (Rough Country 二手極新)', '北部 4x4 零件交流商', 3200, 'https://www.roughcountry.com/floor-mats-cargo-liners/jeep/gladiator/2021'),
            ('Land Rover Discovery / Defender 專用外匯升級避震與越野改裝精品套件', 'Lucky8 LLC 台灣代購組', 28500, 'https://lucky8llc.com/'),
            ('越野四驅車材料零件與全台報廢車殺肉件買賣交流社團', 'Facebook 越野車零件交流社團', 0, 'https://www.facebook.com/groups/325391057802702')
        ]
        
        cursor.executemany('INSERT INTO parts (name, source, price, link) VALUES (?, ?, ?, ?)', dummy_parts)
        conn.commit()
        conn.close()
        print("雲端越野車資料庫初始化成功！")

# 啟動網頁前跑一次更新
init_db_if_not_exists()

@app.route('/')
def index():
    query = request.args.get('query', '')
    brand = request.args.get('brand', '')
    results = []
    
    if query:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if brand and brand != '選擇品牌':
            cursor.execute("SELECT * FROM parts WHERE name LIKE ? AND name LIKE ?", 
                           ('%' + query + '%', '%' + brand + '%'))
        else:
            cursor.execute("SELECT * FROM parts WHERE name LIKE ?", ('%' + query + '%',))
            
        results = cursor.fetchall()
        conn.close()
        
    return render_template('index.html', results=results, query=query, brand=brand)

if __name__ == '__main__':
    app.run()