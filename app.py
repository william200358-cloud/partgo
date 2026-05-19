from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import urllib.parse

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

@app.route('/')
def index():
    query = request.args.get('query', '').strip()
    brand = request.args.get('brand', '')
    results = []
    
    if query:
        # 將中文零件名稱進行網址安全編碼（轉換為 %XX 格式）
        encoded_query = urllib.parse.quote(query)
        
        # 🚀 終極渠道大滿貫：網羅日美台所有越野車、皮卡與二手殺肉核心搜尋路徑
        results = [
            # 💬 【社群交流線】
            {
                'name': f'💬 【FB 買賣貼文直達】全臉書社團關於「{query}」的最新車友拆車、現貨交流貼文現場',
                'source': 'Facebook 二手社團貼文',
                'link': f'https://www.facebook.com/search/posts/?q={encoded_query}'
            },
            # 🇯🇵 【日本外匯線】
            {
                'name': f'🇯🇵 【Up Garage 直擊】日本最大二手汽車零件連鎖店「{query}」外匯避震、二手輪框精品現場',
                'source': 'Up Garage 日本二手大廠',
                'link': f'https://www.upgarage.com/service/ja/stock?keyword={encoded_query}'
            },
            {
                'name': f'🇯🇵 【Croooober 全球速配】日本二手車件大本營，直擊最新日本直送「{query}」殺肉神物',
                'source': 'Croooober 日本二手車件',
                'link': f'https://www.croooober.com/cparts/search?q={encoded_query}'
            },
            {
                'name': f'🇯🇵 【日本 Amazon】日規車型、改裝小配件與原廠「{query}」全新部品即時搜尋現場',
                'source': '日本 Amazon',
                'link': f'https://www.amazon.co.jp/s?k={encoded_query}'
            },
            {
                'name': f'🇯🇵 【日本樂天市場】日本各大改裝廠直營店「{query}」最新進口零件與特裝耗材列表',
                'source': '日本樂天市場',
                'link': f'https://search.rakuten.co.jp/search/mall/{encoded_query}/'
            },
            # 🇺🇸 【美國改裝皮卡線】
            {
                'name': f'🧭 【美國 Quadratec 旗艦】Jeep 藍哥/角鬥士專屬改裝天堂，全美最硬核「{query}」精品庫',
                'source': 'Quadratec 美國 Jeep 聖地',
                'link': f'https://www.quadratec.com/search/{encoded_query}'
            },
            {
                'name': f'🇺🇸 【ExtremeTerrain 越野】豐田 Tacoma、Tundra、福特 Ranger 專攻「{query}」外觀底盤重鎮',
                'source': 'ExtremeTerrain 美國皮卡',
                'link': f'https://www.extremeterrain.com/search?keywords={encoded_query}'
            },
            {
                'name': f'🇺🇸 【4WheelParts 巨頭】全美連鎖越野改裝巨頭，大腳巨獸「{query}」輪框、避震套件直擊',
                'source': '4WheelParts 美國越野',
                'link': f'https://www.4wheelparts.com/s/_/?Ntt={encoded_query}'
            },
            {
                'name': f'🇺🇸 【CARiD 零件百貨】美規車型、改裝與原廠替換用「{query}」全天候精品海路徑',
                'source': 'CARiD 美國汽車百貨',
                'link': f'https://www.carid.com/search/{encoded_query}'
            },
            {
                'name': f'🇺🇸 【美國 Rough Country 直發】皮卡車與越野車專用「{query}」底盤加高、全天候內裝精品',
                'source': 'Rough Country 美國直郵',
                'link': f'https://www.roughcountry.com/search?q={encoded_query}'
            },
            {
                'name': f'🇬🇧 【英國 Lucky8 越野中心】Land Rover Defender / Discovery 專用「{query}」高階底盤外匯件',
                'source': 'Lucky8 LLC 歐美外匯',
                'link': f'https://lucky8llc.com/search?q={encoded_query}'
            },
            {
                'name': f'🌎 【eBay 全球速配】美國/歐洲電商外匯原廠件，全世界絕版老越野車「{query}」零件海',
                'source': 'eBay 全球外匯中心',
                'link': f'https://www.ebay.com/sch/i.html?_nkw={encoded_query}'
            },
            # 🇹🇼 【台灣在地殺肉線】
            {
                'name': f'🦐 【台灣蝦皮現貨】Shopee 跨境與在地賣家「{query}」全新改裝品、二手零件即時比價賣場',
                'source': 'Shopee 蝦皮購物',
                'link': f'https://shopee.tw/search?keyword={encoded_query}'
            },
            {
                'name': f'🏺 【露天老車殺肉庫】Ruten 露天市集全台報廢車殺肉件、拆車現貨「{query}」商品列表',
                'source': 'Ruten 露天市集',
                'link': f'https://www.ruten.com/find/?q={encoded_query}'
            },
            {
                'name': f'🔨 【Yahoo 奇摩拍賣】老字號零件商、報廢外匯車商拆車「{query}」精品在線競標現場',
                'source': 'Yahoo 奇摩拍賣',
                'link': f'https://tw.bid.yahoo.com/search/auction/product?p={encoded_query}'
            },
            {
                'name': f'🌀 【旋轉拍賣 Carousell】二手車友清倉庫存、面交無壓力「{query}」好物個人拍賣版',
                'source': 'Carousell 旋轉拍賣',
                'link': f'https://tw.carousell.com/search/{encoded_query}'
            }
        ]
        
        # 為了統一前台格式，動態卡片價格皆設為 0 (面議/進入現場查看)
        for item in results:
            item['id'] = 'live_search'
            item['price'] = 0
            
        # 🚀 從本機資料庫撈出你手動收集、100% 點擊降落特定商品頁的比比昂與 Japan Yatora 絕對路徑網址
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM parts WHERE name LIKE ? ORDER BY price ASC", ('%' + query + '%',))
        db_rows = cursor.fetchall()
        conn.close()
        
        for row in db_rows:
            results.append({
                'id': row['id'],
                'name': row['name'],
                'source': row['source'],
                'price': row['price'],
                'link': row['link']
            })
        
        # 自動排序：有標價的排前面，面議的動態跳轉卡片排後面
        results.sort(key=lambda x: (x['price'] == 0, x['price']))
        
        # 根據前台下拉選單選取的渠道進行精準過濾
        if brand and brand != '選擇品牌':
            results = [r for r in results if brand in r['source'] or brand in r['name']]
        
    return render_template('index.html', results=results, query=query, brand=brand)

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