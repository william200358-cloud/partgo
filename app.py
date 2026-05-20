from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import urllib.parse
import os
import requests as http_requests

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'partgo-2026')

# eBay Browse API — 填入你的 App ID (Client ID)
EBAY_APP_ID = os.environ.get('EBAY_APP_ID', '')   # 在 Render 環境變數設定

def get_db_connection():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db_if_not_exists():
    try:
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
    except Exception as e:
        print(f"DB init error: {e}")

init_db_if_not_exists()

# ── 翻譯對照表（35+ 組）──────────────────────────────
TRANSLATION_TABLE = [
    (["避震", "懸吊", "減震", "避振", "緩震"],        {"en": "suspension lift kit", "jp": "サスペンション"}),
    (["彈簧", "螺旋彈簧", "板片彈簧"],                 {"en": "coil spring", "jp": "コイルスプリング"}),
    (["避震筒", "避震器"],                              {"en": "shock absorber", "jp": "ショックアブソーバー"}),
    (["輪框", "輪圈", "鋁圈", "鋼圈"],                 {"en": "off-road wheels rims", "jp": "オフロードホイール"}),
    (["輪胎", "越野胎", "MT胎", "AT胎"],               {"en": "off-road tires mud terrain", "jp": "オフロードタイヤ"}),
    (["輪轂", "輪毂蓋"],                               {"en": "wheel hub", "jp": "ホイールハブ"}),
    (["前保桿", "前保"],                               {"en": "front bumper", "jp": "フロントバンパー"}),
    (["後保桿", "後保"],                               {"en": "rear bumper", "jp": "リアバンパー"}),
    (["保桿", "防撞桿", "保險桿"],                     {"en": "bumper", "jp": "バンパー"}),
    (["側步踏板", "踏板", "側踏板"],                   {"en": "running board side step", "jp": "サイドステップ"}),
    (["翼子板", "葉子板", "輪弧"],                      {"en": "fender flare", "jp": "フェンダーフレア"}),
    (["引擎蓋"],                                       {"en": "hood", "jp": "ボンネット"}),
    (["護板", "底盤護板", "skid plate"],               {"en": "skid plate underbody", "jp": "アンダーガード"}),
    (["地墊", "腳踏墊", "地毯", "車內墊"],             {"en": "floor mats all weather", "jp": "フロアマット"}),
    (["車頂架", "行李架", "車頂箱"],                   {"en": "roof rack cargo carrier", "jp": "ルーフラック"}),
    (["帳篷", "車頂帳"],                               {"en": "rooftop tent RTT", "jp": "ルーフテント"}),
    (["絞盤", "電動絞盤"],                             {"en": "electric winch recovery", "jp": "電動ウインチ"}),
    (["牽引鉤", "拖車鉤", "D環"],                      {"en": "tow hook recovery point D-ring", "jp": "牽引フック"}),
    (["沙板", "沙橋"],                                 {"en": "recovery boards MaxTrax", "jp": "リカバリーボード"}),
    (["LED燈", "車燈", "霧燈", "日行燈"],              {"en": "LED light bar off-road", "jp": "LEDライトバー"}),
    (["補助燈", "探照燈", "射燈"],                     {"en": "spot light auxiliary lamp", "jp": "スポットライト"}),
    (["涉水喉", "呼吸管", "進氣管"],                   {"en": "snorkel air intake", "jp": "スノーケル"}),
    (["傳動軸", "萬向節"],                             {"en": "drive shaft universal joint", "jp": "ドライブシャフト"}),
    (["差速器", "差速鎖", "LSD"],                      {"en": "differential locker LSD", "jp": "デフロック"}),
    (["變速箱", "手排", "自排"],                       {"en": "gearbox transmission", "jp": "トランスミッション"}),
    (["空濾", "空氣濾清器"],                           {"en": "air filter intake", "jp": "エアフィルター"}),
    (["機油", "機油濾芯", "油底殼"],                   {"en": "engine oil filter", "jp": "エンジンオイル"}),
    (["水箱", "散熱器"],                               {"en": "radiator cooling", "jp": "ラジエーター"}),
    (["電瓶", "電池", "蓄電池"],                       {"en": "car battery AGM", "jp": "カーバッテリー"}),
    (["座椅", "椅套", "坐墊"],                         {"en": "seat cover bucket seat", "jp": "シートカバー"}),
    (["方向盤", "方向機"],                             {"en": "steering wheel", "jp": "ステアリング"}),
    (["拖車", "掛鉤", "拖車球"],                       {"en": "trailer hitch receiver", "jp": "トレーラーヒッチ"}),
    (["貨台蓋", "皮卡蓋", "硬蓋"],                     {"en": "tonneau cover truck bed cover", "jp": "トノカバー"}),
    (["貨台", "皮卡貨台", "荷台"],                     {"en": "truck bed cargo", "jp": "荷台"}),
]

def translate_keyword(keyword):
    kw = keyword.strip()
    if not kw:
        return {"en": "", "jp": ""}

    en_kw = kw
    jp_kw = kw
    matched = False
    for keywords, result in sorted(
        TRANSLATION_TABLE,
        key=lambda item: max(len(k) for k in item[0]),
        reverse=True
    ):
        for key in sorted(keywords, key=len, reverse=True):
            if key in en_kw or key in jp_kw:
                en_kw = en_kw.replace(key, result["en"])
                jp_kw = jp_kw.replace(key, result["jp"])
                matched = True

    if not matched:
        return {"en": kw, "jp": kw}

    return {
        "en": " ".join(en_kw.split()),
        "jp": " ".join(jp_kw.split()),
    }


# ── eBay Browse API：抓前 5 筆即時商品 ──────────────────
def fetch_ebay_items(en_keyword, limit=5):
    """
    回傳 list of dict:
        title, price, currency, condition, url, image_url
    需要在 Render 環境變數設定 EBAY_APP_ID
    """
    if not EBAY_APP_ID:
        return []
    try:
        url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
        headers = {
            "Authorization": f"Bearer {_get_ebay_token()}",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
            "Content-Type": "application/json",
        }
        params = {
            "q": en_keyword,
            "limit": limit,
            "filter": "itemLocationCountry:US,AU,JP,GB,TW",
        }
        resp = http_requests.get(url, headers=headers, params=params, timeout=6)
        data = resp.json()
        items = []
        for item in data.get("itemSummaries", []):
            price_info = item.get("price", {})
            items.append({
                "title":     item.get("title", ""),
                "price":     price_info.get("value", ""),
                "currency":  price_info.get("currency", "USD"),
                "condition": item.get("condition", ""),
                "url":       item.get("itemWebUrl", ""),
                "image_url": item.get("image", {}).get("imageUrl", ""),
            })
        return items
    except Exception as e:
        print(f"eBay API error: {e}")
        return []

def _get_ebay_token():
    """
    用 Client Credentials flow 取得 OAuth token。
    需要 EBAY_APP_ID（Client ID）和 EBAY_CERT_ID（Client Secret）。
    """
    import base64
    client_id     = EBAY_APP_ID
    client_secret = os.environ.get('EBAY_CERT_ID', '')
    credentials   = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    resp = http_requests.post(
        "https://api.ebay.com/identity/v1/oauth2/token",
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data="grant_type=client_credentials&scope=https://api.ebay.com/oauth/api_scope",
        timeout=8,
    )
    return resp.json().get("access_token", "")


# ── 靜態導航渠道清單（順序：台灣 → 中國 → 日本 → 美國）────────
def build_results(query, translations, brand=''):
    """
    搜尋關鍵字 = 零件翻譯詞 + 車款（若有選）
    順序：🇹🇼 台灣 → 🇨🇳 中國 → 🇯🇵 日本 → 🇺🇸 美國
    """
    # 組合搜尋字串
    en_part = translations["en"]
    jp_part = translations["jp"]
    tw_part = query

    if brand:
        en_full = f"{en_part} {brand}"
        # 日文搜尋保留英文車款，因日本站多能辨識英文車款
        jp_full = f"{jp_part} {brand}"
        tw_full = f"{tw_part} {brand}"
    else:
        en_full = en_part
        jp_full = jp_part
        tw_full = tw_part

    en_query = urllib.parse.quote(en_full)
    jp_query = urllib.parse.quote(jp_full)
    tw_query = urllib.parse.quote(tw_full)

    display_en = en_full
    display_jp = jp_full

    return [
        # ── 🇹🇼 台灣線 ──────────────────────────────────
        {"category": "台灣",
         "name": f'🦐 蝦皮購物 ➔ 搜尋「{tw_full}」在地現貨',
         "source": "Shopee 蝦皮購物", "price_status": "新台幣 / 點進看價",
         "link": f"https://shopee.tw/search?keyword={tw_query}"},
        {"category": "台灣",
         "name": f'🏺 露天市集 ➔ 搜尋「{tw_full}」老車殺肉件',
         "source": "Ruten 露天市集", "price_status": "新台幣 / 點進看價",
         "link": f"https://www.ruten.com/find/?q={tw_query}"},
        {"category": "台灣",
         "name": f'🔨 Yahoo 奇摩拍賣 ➔ 搜尋「{tw_full}」競標現場',
         "source": "Yahoo 奇摩拍賣", "price_status": "新台幣 / 點進看價",
         "link": f"https://tw.bid.yahoo.com/search/auction/product?p={tw_query}"},
        {"category": "台灣",
         "name": f'🌀 Carousell 旋轉拍賣 ➔ 搜尋「{tw_full}」車友面交',
         "source": "Carousell 旋轉拍賣", "price_status": "新台幣 / 點進看價",
         "link": f"https://tw.carousell.com/search/{tw_query}"},
        {"category": "台灣",
         "name": f'💬 Facebook 車友社團 ➔ 進社團搜尋「{tw_full}」',
         "source": "Facebook 越野車友社團", "price_status": "面議 / 私訊",
         "link": "https://www.facebook.com/groups/374536289309519/"},
        # ── 🇨🇳 中國線 ──────────────────────────────────
        {"category": "中國",
         "name": f'🇨🇳 淘寶 ➔ 搜尋「{tw_full}」',
         "source": "淘寶", "price_status": "人民幣計價 / 跨境",
         "link": f"https://s.taobao.com/search?q={tw_query}"},
        # ── 🇯🇵 日本線 ──────────────────────────────────
        {"category": "日本",
         "name": f'🇯🇵 比比昂日本代標 ➔ 搜尋「{display_jp}」',
         "source": "Bibian 比比昂", "price_status": "日幣計價 / 代標",
         "link": f"https://www.bibian.co.jp/search.php?keyword={jp_query}"},
        {"category": "日本",
         "name": f'🇯🇵 Japan Yatora 代購 ➔ 搜尋「{display_jp}」',
         "source": "Japan Yatora", "price_status": "日幣計價 / 跨境",
         "link": f"https://www.bibian.co.jp/search.php?keyword={jp_query}"},
        {"category": "日本",
         "name": f'🇯🇵 Up Garage 日本二手 ➔ 搜尋「{display_jp}」',
         "source": "Up Garage 日本二手", "price_status": "日幣計價 / 二手現貨",
         "link": f"https://www.upgarage.com/service/ja/stock?keyword={jp_query}"},
        {"category": "日本",
         "name": f'🇯🇵 Croooober ➔ 搜尋「{display_jp}」日本直送',
         "source": "Croooober 日本二手", "price_status": "日幣計價 / 海外直郵",
         "link": f"https://www.croooober.com/cparts/search?q={jp_query}"},
        {"category": "日本",
         "name": f'🇯🇵 日本 Amazon ➔ 搜尋「{display_jp}」全新部品',
         "source": "日本 Amazon", "price_status": "日幣計價 / 跨境電商",
         "link": f"https://www.amazon.co.jp/s?k={jp_query}"},
        {"category": "日本",
         "name": f'🇯🇵 Mercari 日本二手 ➔ 搜尋「{display_jp}」',
         "source": "Mercari 日本二手", "price_status": "日幣計價 / 二手拍賣",
         "link": f"https://jp.mercari.com/search?keyword={jp_query}"},
        {"category": "日本",
         "name": f'🇯🇵 日本樂天市場 ➔ 搜尋「{display_jp}」改裝廠直營',
         "source": "日本樂天市場", "price_status": "日幣計價 / 點數折抵",
         "link": f"https://search.rakuten.co.jp/search/mall/{jp_query}/"},
        # ── 🇺🇸 美國線 ──────────────────────────────────
        {"category": "美國",
         "name": f'🧭 Quadratec Jeep 改裝天堂 ➔ 搜尋「{display_en}」',
         "source": "Quadratec 美國 Jeep", "price_status": "美金計價 / 點進看價",
         "link": f"https://www.quadratec.com/search/{en_query}"},
        {"category": "美國",
         "name": f'🇺🇸 Amazon.com ➔ 搜尋「{display_en}」',
         "source": "Amazon.com", "price_status": "美金計價 / 跨境電商",
         "link": f"https://www.amazon.com/s?k={en_query}"},
        {"category": "美國",
         "name": f'🇺🇸 ExtremeTerrain ➔ 搜尋「{display_en}」',
         "source": "ExtremeTerrain 美國皮卡", "price_status": "美金計價 / 點進看價",
         "link": f"https://www.extremeterrain.com/search?keywords={en_query}"},
        {"category": "美國",
         "name": f'🇺🇸 4WheelParts ➔ 搜尋「{display_en}」',
         "source": "4WheelParts 美國越野", "price_status": "美金計價 / 點進看價",
         "link": f"https://www.4wheelparts.com/s/_/?Ntt={en_query}"},
        {"category": "美國",
         "name": f'🇺🇸 CARiD 汽車百貨 ➔ 搜尋「{display_en}」',
         "source": "CARiD 汽車百貨", "price_status": "美金計價 / 點進看價",
         "link": f"https://www.carid.com/search/{en_query}"},
        {"category": "美國",
         "name": f'🇺🇸 Rough Country ➔ 搜尋「{display_en}」底盤套件',
         "source": "Rough Country 底盤", "price_status": "美金計價 / 點進看價",
         "link": f"https://www.roughcountry.com/search?q={en_query}"},
        {"category": "美國",
         "name": f'🇬🇧 Lucky8 路虎越野 ➔ 搜尋「{display_en}」',
         "source": "Lucky8 LLC 歐美外匯", "price_status": "美金計價 / 點進看價",
         "link": f"https://lucky8llc.com/search?q={en_query}"},
    ]


def group_results(results):
    grouped = {"台灣": [], "中國": [], "日本": [], "美國": []}
    for item in results:
        grouped.setdefault(item.get("category", "台灣"), []).append(item)
    return grouped


# ── 路由 ────────────────────────────────────────────────
@app.route('/')
def index():
    query  = request.args.get('query', '').strip()
    brand  = request.args.get('brand', '')
    results      = []
    ebay_items   = []
    translations = {"en": "", "jp": ""}

    if query:
        translations = translate_keyword(query)
        results      = build_results(query, translations, brand=brand)

        # eBay 即時商品：零件英文 + 車款一起搜
        ebay_search = f"{translations['en']} {brand}".strip() if brand else translations["en"]
        ebay_items  = fetch_ebay_items(ebay_search, limit=5)

        # 資料庫私房網址（排最前）
        try:
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM parts WHERE name LIKE ? ORDER BY price ASC",
                           ('%' + query + '%',))
            for row in cursor.fetchall():
                results.insert(0, {
                    "id":           row["id"],
                    "category":     "台灣",
                    "name":         row["name"],
                    "source":       row["source"],
                    "price_status": "面議" if row["price"] == 0 else f"NT$ {row['price']}",
                    "price":        row["price"],
                    "link":         row["link"],
                })
            conn.close()
        except Exception as e:
            print(f"DB query error: {e}")

        for item in results:
            item.setdefault("id", "live")
            item.setdefault("price", 0)

    return render_template("index.html",
                           results=results,
                           ebay_items=ebay_items,
                           grouped_results=group_results(results),
                           query=query,
                           brand=brand,
                           translations=translations,
                           ebay_configured=bool(EBAY_APP_ID))


# ── 後台（無密碼）───────────────────────────────────────
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'POST':
            cursor.execute(
                'INSERT INTO parts (name, source, price, link) VALUES (?, ?, ?, ?)',
                (request.form['name'], request.form['source'],
                 request.form['price'], request.form['link'])
            )
            conn.commit()
            flash('✅ 已新增成功！')
            return redirect(url_for('admin'))

        cursor.execute('SELECT * FROM parts ORDER BY id DESC')
        all_parts = cursor.fetchall()
        conn.close()
    except Exception as e:
        all_parts = []
        flash(f'資料庫錯誤：{e}')

    return render_template('admin.html', all_parts=all_parts)


@app.route('/admin/delete/<int:part_id>', methods=['POST'])
def delete_part(part_id):
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM parts WHERE id = ?', (part_id,))
        conn.commit()
        conn.close()
        flash('🗑️ 已刪除')
    except Exception as e:
        flash(f'刪除失敗：{e}')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(debug=False)
