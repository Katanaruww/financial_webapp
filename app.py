from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Инициализация базы
def init_db():
    conn = sqlite3.connect('/data/finance.db')

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
    conn = sqlite3.connect('/data/finance.db')

    cur = conn.cursor()
    cur.execute('''
        INSERT INTO expenses (user_id, title, category, amount, important, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        1,
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
    conn = sqlite3.connect('/data/finance.db')

    cur = conn.cursor()
    cur.execute('''
        INSERT INTO incomes (user_id, title, amount, date)
        VALUES (?, ?, ?, ?)
    ''', (
        1,
        data['title'],
        data['amount'],
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    return jsonify({"message": "Доход сохранён"})


@app.route('/api/report', methods=['GET'])
def report():
    user_id = 1
    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    conn = sqlite3.connect('/data/finance.db')
  # или './finance.db' если без Render-диска
    cur = conn.cursor()

    cur.execute("SELECT title, amount, date FROM incomes WHERE user_id = 1")
    incomes = cur.fetchall()

    cur.execute("SELECT title, category, amount, important, date FROM expenses WHERE user_id = 1"))
    expenses = cur.fetchall()

    conn.close()

    return jsonify({
        "incomes": incomes,
        "expenses": expenses
    })
    print("📦 Получен запрос на отчёт")
    print("Доходы:")
    print(incomes)
    print("Траты:")
    print(expenses)
if __name__ == '__main__':
    app.run(debug=True, port=8080)

