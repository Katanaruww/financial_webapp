from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Инициализация базы
def init_db():
    conn = sqlite3.connect('finance.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            category TEXT,
            amount REAL,
            important BOOLEAN,
            date TEXT
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            amount REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/api/expense', methods=['POST'])
def add_expense():
    data = request.json
    conn = sqlite3.connect('finance.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO expenses (user_id, title, category, amount, important, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['user_id'],
        data['title'],
        data['category'],
        data['amount'],
        data.get('important', False),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Трата сохранена"})

@app.route('/api/income', methods=['POST'])
def add_income():
    data = request.json
    print("INCOME:", data)
    conn = sqlite3.connect('finance.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO incomes (user_id, title, amount, date)
        VALUES (?, ?, ?, ?)
    ''', (
        data['user_id'],
        data['title'],
        data['amount'],
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Доход сохранён"})

if __name__ == '__main__':
    app.run(debug=True, port=8080)

