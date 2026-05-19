from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

# 🛠️ 資料庫清洗點火：注入 100% 純汽車各種二手/改裝零件數據
def init_db_if_not_exists():
    if True:  
        print("正在為雲端注入純車輛零件比價大數據...")
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
        
        # 🎯 圍繞真實渠道衍生出的車輛各種零件比價清單
        dummy_parts = [
            # 1. 腳踏墊 / 地墊類零件
            ('Jeep Gladiator (2021) 專用全天候防水腳踏墊 (Rough Country 美國直郵代購件)', '美國 Rough Country 原廠', 3200, 'https://www.roughcountry.com/floor-mats-cargo-liners/jeep/gladiator/2021'),
            ('Jeep Wrangler / Gladiator 專用防滑耐磨橡膠地墊 (車友二手出清)', 'Facebook 跨境零件交流社團', 1800, 'https://www.facebook.com/groups/325391057802702'),
            
            # 2. 懸吊 / 避震器類零件
            ('鈴木 Suzuki Jimny JB74 專用外匯進口升級避震器加高套件 (比比昂日本代標現貨)', 'Bibian 比比昂 - 日本Yahoo拍賣代標', 18500, 'https://share.google/EfGnvwfS0FMLQY9gs'),
            ('Land Rover Discovery 專用高階越野懸吊避震系統改裝精品減震筒 (海外直送)', 'Lucky8 LLC 全球越野中心', 26000, 'https://lucky8llc.com/'),
            ('Land Rover Defender 2020+ 專用外匯越野升級避震器套件 (全新進口)', 'Lucky8 LLC 全球越野中心', 28500, 'https://lucky8llc.com/'),
            
            # 3. 外觀 / 防撞桿 / 車頂架 / 輪框殺肉件
            ('Toyota Hilux 海拉克斯專用美規前保桿加重防撞桿 (日本外匯精品)', 'Bibian 比比昂 - 日本Yahoo拍賣代標', 15000, 'https://share.google/EfGnvwfS0FMLQY9gs'),
            ('Suzuki Jimny 專用輕量化鋁合金雙層防雨車頂行李架 (側邊附爬梯梯子)', 'Bibian 比比昂 - 日本Yahoo拍賣代標', 8500, 'https://share.google/EfGnvwfS0FMLQY9gs'),
            ('Jeep 藍哥 Wrangler 專用外匯 17 吋越野防脫圈輪框 (四輪組面議)', 'Facebook 跨境零件交流社團', 0, 'https://www.facebook.com/groups/325391057802702'),
            
            # 4. 報廢車通用殺肉專區
            ('全球四驅越野車、皮卡車外匯殺肉件與二手車輛零件買賣交流社團', 'Facebook 跨境零件交流社團', 0, 'https://www.facebook.com/groups/325391057802702')
        ]
        
        cursor.executemany('INSERT INTO parts (name, source, price, link) VALUES (?, ?, ?, ?)', dummy_parts)
        conn.commit()
        conn.close()
        print("純車輛零件比價數據注入成功！")

init_db_if_not_exists()

# 🔍 前台搜尋大腦（智慧防空擋機制已改為純車輛導航）
@app.route('/')
def index():
    query = request.args.get('query', '').strip()
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
            
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # 🚀 防空擋救援：搜到太冷門的汽車零件，自動導向真實汽車代購渠道搜尋
        if len(results) == 0:
            results = [
                {
                    'id': 999,
                    'name': f'【日本外匯車件】您搜尋的汽車零件「{query}」代標現場！點擊同步日本 Yahoo 拍賣最新殺肉件',
                    'source': 'Bibian 比比昂 日本代標',
                    'price': 0,
                    'link': 'https://share.google/EfGnvwfS0FMLQY9gs'
                },
                {
                    'id': 998,
                    'name': f'【美國原廠直送】「{query}」Jeep、皮卡全系列車款原廠升級件與全天候改裝精品直發台灣',
                    'source': 'Rough Country / 美國直郵',
                    'price': 0,
                    'link': 'https://www.roughcountry.com/floor-mats-cargo-liners/jeep/gladiator/2021'
                },
                {
                    'id': 997,
                    'name': f'【歐美越野精品】「{query}」Land Rover 衛士/發現系列高階懸吊、底盤外匯零件全球速配',
                    'source': 'Lucky8 LLC 歐美代購',
                    'price': 0,
                    'link': 'https://lucky8llc.com/'
                }
            ]
        
    return render_template('index.html', results=results, query=query, brand=brand)

# 🛠️ 後台管理
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