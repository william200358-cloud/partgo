from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('parts.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    query = request.args.get('query', '')
    brand = request.args.get('brand', '')
    results = []
    
    # 只要有輸入關鍵字，就進行查詢
    if query:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 如果使用者有選品牌，且不是預設的「選擇品牌」
        if brand and brand != '選擇品牌':
            cursor.execute("SELECT * FROM parts WHERE name LIKE ? AND name LIKE ?", 
                           ('%' + query + '%', '%' + brand + '%'))
        else:
            # 如果沒選品牌，就單純查關鍵字
            cursor.execute("SELECT * FROM parts WHERE name LIKE ?", ('%' + query + '%',))
            
        results = cursor.fetchall()
        conn.close()
        
    return render_template('index.html', results=results, query=query, brand=brand)

if __name__ == '__main__':
    app.run()