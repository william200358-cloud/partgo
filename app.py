from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

# 🛠️ 雲端自動點火防呆：如果資料庫不存在，自動建立並寫入資料
def init_db_if_not_exists():
    if True:
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
        
       dummy_parts = [
            ('Suzuki Jimny JB74 專用大顆粒全地形越野胎 (BFGoodrich KO2 / 八成新)', '外匯越野改裝精品', 4500, 'https://example.com/tire'),
            ('Jeep Wrangler 藍哥專用前保桿加重防撞桿 (附絞盤座/殺肉件)', '悍馬越野報廢場', 12000, 'https://example.com/bumper'),
            ('Toyota Hilux 海拉克斯專用防滾籠與後斗貨架 (二手極新)', '北部 4x4 零件整合商', 18000, 'https://example.com/rack'),
            ('Jimny 專用加大終傳比齒輪箱 (改大胎重拖救星)', '外匯越野改裝精品', 8500, 'https://example.com/gear'),
            ('越野車通用避震器升高套件 (2吋防傾桿+減震筒組)', '凱汰二手零件王', 15000, 'https://example.com/suspension')
        ]
        
        cursor.executemany('INSERT INTO parts (name, source, price, link) VALUES (?, ?, ?, ?)', dummy_parts)
        conn.commit()
        conn.close()
        print("雲端資料庫初始化成功！")

# 啟動網頁前先跑一次檢查
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