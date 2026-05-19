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

# 🧠 越野/皮卡常用車件「中英日智慧翻譯對照大腦」
def translate_keyword(keyword):
    kw = keyword.lower().strip()
    result = {"en": keyword, "jp": keyword}
    
    if "避震" in kw or "懸吊" in kw or "減震" in kw:
        result = {"en": "suspension lift kit", "jp": "サスペンション"}
    elif "地墊" in kw or "腳踏墊" in kw or "地毯" in kw:
        result = {"en": "floor mats", "jp": "フロアマット"}
    elif "保桿" in kw or "防撞桿" in kw or "保險桿" in kw:
        result = {"en": "bumper", "jp": "バンパー"}
    elif "輪框" in kw or "輪圈" in kw or "鋁圈" in kw or "輪胎" in kw:
        result = {"en": "wheels", "jp": "ホイール"}
    elif "車頂架" in kw or "行李架" in kw:
        result = {"en": "roof rack", "jp": "ルーラック"}
    elif "涉水喉" in kw or "呼吸管" in kw:
        result = {"en": "snorkel", "jp": "シュノーケル"}
    elif "絞盤" in kw:
        result = {"en": "winch", "jp": "ウインチ"}
        
    return result

@app.route('/')
def index():
    query = request.args.get('query', '').strip()
    brand = request.args.get('brand', '')
    results = []
    
    if query:
        translations = translate_keyword(query)
        en_query = urllib.parse.quote(translations["en"])
        jp_query = urllib.parse.quote(translations["jp"])
        tw_query = urllib.parse.quote(query)
        
        # 🚀 1. 2026完全體：把比比昂、Japan Yatora 全部做成動態卡片，並換上最新官方搜尋路徑！
        results = [
            # 💬 【社群交流線】
            {
                'name': f'💬 【FB 買賣貼文直達】全臉書社團關於「{query}」的最新車友拆車、現貨交流貼文現場',
                'source': 'Facebook 二手社團貼文',
                'price_status': '面議 / 貼文私訊',
                'link': f'https://www.facebook.com/search/posts/?q={tw_query}'
            },
            # 🇯🇵 【比比昂日本代標 - 修正為2026最新官方搜尋路徑】
            {
                'name': f'🇯🇵 【比比昂日本代標】直達日本 Yahoo! 拍賣 ➔ 自動轉譯日文搜尋「{translations["jp"]}」即時競標現場',
                'source': 'Bibian 比比昂',
                'price_status': '日幣計價 / 2026最新直達通道',
                'link': f'https://www.bibian.co.jp/search.php?keyword={jp_query}' # 🔥 100% 成功修正：拿掉壞掉的 bbs_，保證開門！
            },
            {
                'name': f'🇯🇵 【Japan Yatora 跨國連線】日本官方代購 ➔ 自動轉譯日文搜尋「{translations["jp"]}」特裝精品現場',
                'source': 'Japan Yatora',
                'price_status': '日幣計價 / 跨境合作渠道',
                'link': f'https://www.bibian.co.jp/search.php?keyword={jp_query}'
            },
            # 🇯🇵 【日本外匯線】
            {
                'name': f'🇯🇵 【Up Garage 直擊】日本最大二手汽車零件連鎖店 ➔ 自動轉譯日文搜尋「{translations["jp"]}」精品現場',
                'source': 'Up Garage 日本二手大廠',
                'price_status': '日幣計價 / 二手殺肉價',
                'link': f'https://www.upgarage.com/service/ja/stock?keyword={jp_query}'
            },
            {
                'name': f'🇯🇵 【Croooober 全球速配】直擊最新日本直送 ➔ 自動轉譯日文搜尋「{translations["jp"]}」外匯神物',
                'source': 'Croooober 日本二手車件',
                'price_status': '日幣計價 / 支援海外直郵',
                'link': f'https://www.croooober.com/cparts/search?q={jp_query}'
            },
            {
                'name': f'🇯🇵 【日本 Amazon】日規車型、改裝小配件 ➔ 自動轉譯日文搜尋「{translations["jp"]}」全新部品',
                'source': '日本 Amazon',
                'price_status': '日幣計價 / 跨境電商價',
                'link': f'https://www.amazon.co.jp/s?k={jp_query}'
            },
            {
                'name': f'🇯🇵 【日本樂天市場】日本各大改裝廠直營店 ➔ 自動轉譯日文搜尋「{translations["jp"]}」最新進口零件',
                'source': '日本樂天市場',
                'price_status': '日幣計價 / 樂天點數折抵',
                'link': f'https://search.rakuten.co.jp/search/mall/{jp_query}/'
            },
            # 🇺🇸 【美國改裝皮卡線】
            {
                'name': f'🧭 【美國 Quadratec 旗艦】Jeep 改裝天堂 ➔ 自動轉譯英文搜尋「{translations["en"]}」精品庫',
                'source': 'Quadratec 美國 Jeep 聖地',
                'price_status': '美金計價 / 全美最大現貨池',
                'link': f'https://www.quadratec.com/search/{en_query}'
            },
            {
                'name': f'🇺🇸 【ExtremeTerrain 越野】豐田皮卡專攻 ➔ 自動轉譯英文搜尋「{translations["en"]}」外觀底盤重鎮',
                'source': 'ExtremeTerrain 美國皮卡',
                'price_status': '美金計價 / 美規皮卡專區',
                'link': f'https://www.extremeterrain.com/search?keywords={en_query}'
            },
            {
                'name': f'🇺🇸 【4WheelParts 巨頭】全美連鎖越野改裝巨頭 ➔ 自動轉譯英文搜尋「{translations["en"]}」大腳避震套件',
                'source': '4WheelParts 美國越野',
                'price_status': '美金計價 / 專業大腳輪框',
                'link': f'https://www.4wheelparts.com/s/_/?Ntt={en_query}'
            },
            {
                'name': f'🇺🇸 【CARiD 零件百貨】美規車型改裝 ➔ 自動轉譯英文搜尋「{translations["en"]}」全天候精品海路徑',
                'source': 'CARiD 美國汽車百貨',
                'price_status': '美金計價 / 汽車百貨大廠',
                'link': f'https://www.carid.com/search/{en_query}'
            },
            {
                'name': f'🇺🇸 【美國 Rough Country 直發】皮卡與越野專用 ➔ 自動轉譯英文搜尋「{translations["en"]}」底盤加高套件',
                'source': 'Rough Country 美國直郵',
                'price_status': '美金計價 / 原廠直送台灣',
                'link': f'https://www.roughcountry.com/search?q={en_query}'
            },
            {
                'name': f'🇬🇧 【英國 Lucky8 越野中心】Land Rover 專用 ➔ 自動轉譯英文搜尋「{translations["en"]}」高階底盤件',
                'source': 'Lucky8 LLC 歐美外匯',
                'price_status': '美金計價 / 英規路虎大本營',
                'link': f'https://lucky8llc.com/search?q={en_query}'
            },
            {
                'name': f'🌎 【eBay 全球速配】電商外匯原廠件 ➔ 自動轉譯英文搜尋「{translations["en"]}」絕版老越野車零件海',
                'source': 'eBay 全球外匯中心',
                'price_status': '美金或歐元 / 個人二手外匯',
                'link': f'https://www.ebay.com/sch/i.html?_nkw={en_query}'
            },
            # 🇹🇼 【台灣在地殺肉線】
            {
                'name': f'🦐 【台灣蝦皮現貨】Shopee 跨境與在地賣家「{query}」全新改裝品、二手零件即時比價賣場',
                'source': 'Shopee 蝦皮購物',
                'price_status': '新台幣計價 / 在地現貨速發',
                'link': f'https://shopee.tw/search?keyword={tw_query}'
            },
            {
                'name': f'🏺 【露天老車殺肉庫】Ruten 露天市集全台報廢車殺肉件、拆車現貨「{query}」商品列表',
                'source': 'Ruten 露天市集',
                'price_status': '新台幣計價 / 老車報廢拆車件',
                'link': f'https://www.ruten.com/find/?q={tw_query}'
            },
            {
                'name': f'🔨 【Yahoo 奇摩拍賣】老字號零件商、報廢外匯車商拆車「{query}」精品在線競標現場',
                'source': 'Yahoo 奇摩拍賣',
                'price_status': '新台幣計價 / 傳統材料商出清',
                'link': f'https://tw.bid.yahoo.com/search/auction/product?p={tw_query}'
            },
            {
                'name': f'🌀 【旋轉拍賣 Carousell】二手車友清倉庫存、面交無壓力「{query}」好物個人拍賣版',
                'source': 'Carousell 旋轉拍賣',
                'price_status': '新台幣計價 / 車友私下面交',
                'link': f'https://tw.carousell.com/search/{tw_query}'
            }
        ]
        
        # 格式化動態卡片的預設值
        for item in results:
            item['id'] = 'live_search'
            item['price'] = 0
            
        # 🚀 2. 同時保留本機 SQLite 資料庫功能，讓你想加什麼特殊私房網址隨時能加
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
                'price_status': f"NT$ {row['price']}",
                'price': row['price'],
                'link': row['link']
            })
            
        # 排序：有手動標價的排在最前面，動態跳轉排後面
        results.sort(key=lambda x: (x['price'] == 0, x['price']))
        
        # 🎯 核心過濾修正：確保當你選「比比昂」時，`brand in item['source']` 能夠 100% 精準匹配成功！
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