from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import urllib.parse  # 引入編碼工具，防止中文亂碼

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db_if_not_exists():
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
    conn.commit()
    conn.close()

init_db_if_not_exists()

# 🔍 前台核心：發動「智慧網址參數空降引擎」
@app.route('/')
def index():
    query = request.args.get('query', '').strip()
    brand = request.args.get('brand', '')
    results = []
    
    if query:
        # 🎯 將中文字轉化為網頁看懂的編碼（例如：避震 -> %E9%81%BF%E9%9C%87）
        encoded_query = urllib.parse.quote(query)
        
        # 🚀 既然對方擋 API，我們就直接用對方的「真實搜尋頁面網址」進行逆向參數注入！
        # 這樣能 100% 保證使用者點擊時，直接在比比昂和歐美官網看見該零件的最新即時搜尋結果！
        results = [
            {
                'id': 1,
                'name': f'【日本 Yahoo 拍賣現場】查看最新「{query}」二手外匯殺肉件與即時競標品',
                'source': 'Bibian 比比昂 日本代標',
                'price': 0, 
                # 🔥 修正為比比昂官方標準公開的搜尋路徑
                'link': f'https://www.bibian.co.jp/bbs_search.php?keyword={encoded_query}' 
            },
            {
                'id': 2,
                'name': f'【美國原廠直送】前往 Rough Country 官網查看專屬「{query}」全天候改裝精品爆款',
                'source': 'Rough Country 美國直郵',
                'price': 0,
                'link': f'https://www.roughcountry.com/search?q={encoded_query}' 
            },
            {
                'id': 3,
                'name': f'【歐美越野精品】前往 Lucky8 尋找 Land Rover 專用底盤懸吊、高階「{query}」外匯升級件',
                'source': 'Lucky8 LLC 歐美外匯',
                'price': 0,
                'link': f'https://lucky8llc.com/search?q={encoded_query}' 
            },
            {
                'id': 4,
                'name': f'【台灣現貨車友交流】前往臉書跨境越野四驅、皮卡外匯通用「{query}」零件買賣社團',
                'source': 'Facebook 跨境零件交流社團',
                'price': 0,
                'link': f'https://www.facebook.com/groups/325391057802702'
            }
        ]
        
        # 根據前台選擇的品牌/渠道進行過濾
        if brand and brand != '選擇品牌':
            results = [r for r in results if brand in r['source'] or brand in r['name']]
        
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