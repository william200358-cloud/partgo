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
        
        dummy_parts = [
            ('汽車發電機 (全新原廠代工件)', '大台北汽車材料', 2800, 'https://example.com/1'),
            ('外匯進口高品質發電機 (保固半年)', '凱汰二手零件王', 1500, 'https://example.com/2'),
            ('BMW E46 M3 原廠真皮賽車椅子 (一對)', '外匯雙B殺肉廠', 35000, 'https://example.com/5'),
            ('BMW 尊榮全功能電動調整座椅', '極致汽車改裝', 18000, 'https://example.com/6')
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