from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

# 🛠️ 建立乾淨的資料庫表格
def init_db_if_not_exists():
    conn = sqlite3.connect('parts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source TEXT NOT NULL,
            price INTEGER NOT NULL,
            link TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

init_db_if_not_exists()

# 🕷️ 核心升級：自動爬取 Lucky8 網站零件的爬蟲大腦
def crawl_lucky8():
    url = "https://lucky8llc.com/collections/defender-2020" # 以經典越野車 Defender 專區為例
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 找到網頁上所有的商品卡片區塊（根據 Lucky8 的 Shopify 網頁結構簡化解析）
            products = soup.select('.product-card, .grid-view-item, .product-item')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            crawl_count = 0
            for prod in products:
                # 抓取商品名稱
                name_tag = prod.select_one('.product-card__title, .grid-view-item__title, .title')
                # 抓取商品價格
                price_tag = prod.select_one('.price-item--regular, .money')
                # 抓取商品連結
                link_tag = prod.select_one('a')
                
                if name_tag and price_tag and link_tag:
                    name = name_tag.text.strip()
                    raw_price = price_tag.text.strip()
                    # 把美金符號與逗號去掉，轉成純數字（例如 $1,250.00 -> 1250）
                    try:
                        price = int(float(raw_price.replace('$', '').replace(',', '').strip()))
                    except:
                        price = 0
                        
                    raw_link = link_tag.get('href', '')
                    link = f"https://lucky8llc.com{raw_link}" if raw_link.startswith('/') else raw_link
                    
                    # 寫入資料庫（若網址重複則自動忽略，避免重複塞入）
                    cursor.execute('''
                        INSERT OR IGNORE INTO parts (name, source, price, link)
                        VALUES (?, ?, ?, ?)
                    ''', (name, "Lucky8 LLC 外匯零件", price, link))
                    crawl_count += 1
            
            conn.commit()
            conn.close()
            return f"成功自動爬取並更新了 {crawl_count} 筆 Lucky8 越野零件數據！"
    except Exception as e:
        return f"爬蟲引擎罷工原因: {str(e)}"
    return "未能成功抓取數據。"

# 🔍 前台：搜尋首頁（核心變更：加上 ORDER BY price ASC 達成真正比價排序）
@app.route('/')
def index():
    query = request.args.get('query', '')
    brand = request.args.get('brand', '')
    results = []
    
    if query:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 💡 真正的比價秘密：SQL 尾端加上 ORDER BY price ASC，讓最便宜的排在最上面！
        if brand and brand != '選擇品牌':
            cursor.execute("SELECT * FROM parts WHERE name LIKE ? AND name LIKE ? ORDER BY price ASC", 
                           ('%' + query + '%', '%' + brand + '%'))
        else:
            cursor.execute("SELECT * FROM parts WHERE name LIKE ? ORDER BY price ASC", ('%' + query + '%',))
            
        results = cursor.fetchall()
        conn.close()
        
    return render_template('index.html', results=results, query=query, brand=brand)

# 🛠️ 後台：進化成「爬蟲控制面板」
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    message = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'run_crawler':
            # 按下按鈕時，立刻發動爬蟲大腦出擊
            message = crawl_lucky8()
            
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM parts ORDER BY id DESC')
    all_parts = cursor.fetchall()
    conn.close()
    return render_template('admin.html', all_parts=all_parts, message=message)

if __name__ == '__main__':
    app.run()