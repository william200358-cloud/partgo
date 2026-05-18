import sqlite3

conn = sqlite3.connect('parts.db')
cursor = conn.cursor()

# 建立零件資料表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        source TEXT NOT NULL,
        price INTEGER NOT NULL,
        link TEXT
    )
''')

# 寫入預設的比價數據
dummy_parts = [
    ('汽車發電機 (全新原廠代工件)', '大台北汽車材料', 2800, 'https://example.com/1'),
    ('外匯進口高品質發電機 (保固半年)', '凱汰二手零件王', 1500, 'https://example.com/2'),
    ('整新品汽車發電機 (交大材料行)', 'BigGo 零件整合商', 1800, 'https://example.com/3'),
    ('汽車發電機 12V 高規格', '蝦皮優選車配', 2100, 'https://example.com/4')
]

cursor.executemany('INSERT INTO parts (name, source, price, link) VALUES (?, ?, ?, ?)', dummy_parts)
conn.commit()
conn.close()

print("PartGo 資料庫初始化成功！已匯入多來源比價數據。")