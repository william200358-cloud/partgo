from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import requests
from bs4 import BeautifulSoup
import re

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
            link TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

init_db_if_not_exists()

# 🕷️ 核心引擎：即時聯網爬取比比昂（日本Yahoo拍賣）精準商品頁面
def fetch_live_bibian_data(keyword):
    # 建立比比昂日本Yahoo拍賣的真實搜尋網址
    search_url = f"https://www.bibian.co.jp/bbs_search.php?keyword={keyword}"
    
    # 偽裝成一般 iPhone/Chrome 瀏覽器標頭，防止機房 IP 被擋
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    scraped_results = []
    
    try:
        # 1. 帶著關鍵字直奔現場
        response = requests.get(search_url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. 根據比比昂目前的網頁結構，精準定位每一個商品的卡片區塊
            # (實務上代標網多以 items, product-box 或 li 呈現，這裡採用通用解析邏輯)
            items = soup.select('.product_box, .item, .search_result_li, li')
            
            for item in items:
                # A. 抓取精準的商品名稱
                title_tag = item.select_one('.title, .item_name, a')
                # B. 抓取直覺的價格（包含日幣或已換算台幣的數字）
                price_tag = item.select_one('.price, .current_price, .money')
                # C. 核心關鍵：抓取該商品「精準的詳情頁面網址」
                link_tag = item.select_one('a')
                
                if title_tag and price_tag and link_tag:
                    name = title_tag.text.strip()
                    raw_price = price_tag.text.strip()
                    raw_link = link_tag.get('href', '')
                    
                    # 過濾掉非目標的雜訊連結
                    if not raw_link or 'javascript' in raw_link or len(name) < 3:
                        continue
                        
                    # 補全相對路徑網址，變成絕對能點轉的「精準網址」
                    if raw_link.startswith('/'):
                        full_link = f"https://www.bibian.co.jp{raw_link}"
                    else:
                        full_link = raw_link
                    
                    # 清洗價格文字，只留下純數字 (例如 NT$ 1,500 -> 1500)
                    digits = re.findall(r'\d+', raw_price.replace(',', ''))
                    price = int(digits[0]) if digits else 0
                    
                    # 只要有名稱、價格與精準網址，就視為有效比價資料
                    if price > 0 and name:
                        scraped_results.append({
                            'name': name,
                            'source': '比比昂日本代標 (Yahoo!)',
                            'price': price,
                            'link': full_link
                        })
                        
                # 為了搜尋速度，第一階段即時抓取前 10 筆最精準的資料即可
                if len(scraped_results) >= 10:
                    break
    except Exception as e:
        print(f"即時聯網抓取發生小插曲: {str(e)}")
        
    return scraped_results

# 🔍 前台大腦：只要輸入關鍵字，立刻發動即時動態爬蟲
@app.route('/')
def index():
    query = request.args.get('query', '').strip()
    brand = request.args.get('brand', '')
    results = []
    
    if query:
        # 🚀 第一步：即時發動跨海爬蟲，直奔比比昂代標現場抓取「精準網址」商品
        live_data = fetch_live_bibian_data(query)
        
        # 🚀 第二步：將剛剛即時抓到的最新網址與價格，暫存進雲端資料庫（自動過濾重複）
        conn = get_db_connection()
        cursor = conn.cursor()
        for item in live_data:
            cursor.execute('''
                INSERT OR IGNORE INTO parts (name, source, price, link)
                VALUES (?, ?, ?, ?)
            ''', (item['name'], item['source'], item['price'], item['link']))
        conn.commit()
        
        # 🚀 第三步：從資料庫撈出包含該關鍵字的所有零件，並依價格「低到高自動比價排序」
        if brand and brand != '選擇品牌':
            cursor.execute("SELECT * FROM parts WHERE name LIKE ? AND name LIKE ? ORDER BY price ASC", 
                           ('%' + query + '%', '%' + brand + '%'))
        else:
            cursor.execute("SELECT * FROM parts WHERE name LIKE ? ORDER BY price ASC", ('%' + query + '%',))
            
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
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