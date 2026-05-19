from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

# 🛠️ 雲端自動點火防呆（把之前的 True 改回原本的偵測，讓未來手動新增的資料不會被沖掉）
def init_db_if_not_exists():
    if not os.path.exists('parts.db'):
        print("偵測到雲端未建立資料庫，正在自動初始化...")
        conn = sqlite3.connect('parts.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                source TEXT NOT NULL,
                price INTEGER NOT NULL,
                link TEXT
            )
        ''')
        
        # 初始預設放這三筆真實網址
        dummy_parts = [
            ('Jeep Gladiator (2021) 專用全天候防水腳踏墊 / 後行李箱襯墊 (Rough Country 二手極新)', '北部 4x4 零件交流商', 3200, 'https://www.roughcountry.com/floor-mats-cargo-liners/jeep/gladiator/2021'),
            ('Land Rover Discovery / Defender 專用外匯升級避震與越野改裝精品套件', 'Lucky8 LLC 台灣代購組', 28500, 'https://lucky8llc.com/'),
            ('越野四驅車材料零件與全台報廢車殺肉件買賣交流社團', 'Facebook 越野車零件交流社團', 0, 'https://www.facebook.com/groups/325391057802702')
        ]
        
        cursor.executemany('INSERT INTO parts (name, source, price, link) VALUES (?, ?, ?, ?)', dummy_parts)
        conn.commit()
        conn.close()
        print("雲端資料庫初始化成功！")

# 啟動網頁前跑一次檢查
init_db_if_not_exists()

# 🔍 前台：搜尋首頁
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

# 🛠️ 後台：管理頁面（查看與新增零件）
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 如果使用者按下「確認新增」，會走 POST 路由送出表單
    if request.method == 'POST':
        name = request.form['name']
        source = request.form['source']
        price = request.form['price']
        link = request.form['link']
        
        # 把新零件塞進資料庫
        cursor.execute('INSERT INTO parts (name, source, price, link) VALUES (?, ?, ?, ?)',
                       (name, source, price, link))
        conn.commit()
        return redirect(url_for('admin')) # 新增完重新整理後台頁面
        
    # 平時進去後台（GET），會撈出目前資料庫所有的零件列在下方
    cursor.execute('SELECT * FROM parts ORDER BY id DESC')
    all_parts = cursor.fetchall()
    conn.close()
    return render_template('admin.html', all_parts=all_parts)

if __name__ == '__main__':
    app.run()