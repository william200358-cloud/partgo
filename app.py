from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import urllib.parse  # 核心工具：負責把中文零件安全編碼，防止跳轉時變亂碼

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

# 🔍 前台核心：發動「全網搜尋引擎超連結注入大腦」
@app.route('/')
def index():
    query = request.args.get('query', '').strip()
    brand = request.args.get('brand', '')
    results = []
    
    if query:
        # 🎯 將中文字（例如：避震器、地墊）編碼成網址專用字串
        encoded_query = urllib.parse.quote(query)
        
        # 🚀 史詩級升級：直接向各大電商與社交龍頭的核心搜尋引擎「借道」
        # 只要使用者點擊「前往查看」，就會帶著關鍵字強制空降到該平台的商品/貼文海鮮現場！
        results = [
            {
                'id': 1,
                'name': f'💬 【FB 買賣貼文直達】全臉書所有越野社團關於「{query}」的最新售價、殺肉交流貼文列表',
                'source': 'Facebook 二手社團貼文現場',
                'price': 0, # 貼文價格多變，顯示即時面議
                'link': f'https://www.facebook.com/search/posts/?q={encoded_query}' # 🔥 核心黑科技：直接直擊全網 FB 貼文，而不是社團首頁！
            },
            {
                'id': 2,
                'name': f'🇯🇵 【日本外匯一件代標】比比昂 Yahoo! 拍賣「{query}」日本在地二手、報廢場殺肉精品競標現場',
                'source': 'Bibian 比比昂 日本代標',
                'price': 0,
                'link': f'https://www.bibian.co.jp/bbs_search.php?keyword={encoded_query}' # 🔥 100% 成功修正後的官方公開搜尋跳轉路徑
            },
            {
                'id': 3,
                'name': f'🦐 【台灣蝦皮現貨】Shopee 跨境與在地賣家「{query}」全新改裝品、二手零件即時比價賣場',
                'source': 'Shopee 蝦皮購物',
                'price': 0,
                'link': f'https://shopee.tw/search?keyword={encoded_query}' # 🔥 一鍵空降蝦皮搜尋現場！
            },
            {
                'id': 4,
                'name': f'🏺 【露天老車殺肉庫】Ruten 露天市集全台報廢車殺肉件、拆車現貨「{query}」商品列表',
                'source': 'Ruten 露天市集',
                'price': 0,
                'link': f'https://www.ruten.com/find/?q={encoded_query}' # 🔥 一鍵空降露天搜尋現場！
            },
            {
                'id': 5,
                'name': f'🇺🇸 【美規改裝大廠外匯】美國 eBay 全球速配「{query}」Jeep、皮卡原廠升級件與全天候精品',
                'source': 'eBay 全球外匯中心',
                'price': 0,
                'link': f'https://www.ebay.com/sch/i.html?_nkw={encoded_query}' # 🔥 一鍵空降美規 eBay 搜尋現場！
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