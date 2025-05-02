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
    user_id = 1  # фиксированный ID
    conn = sqlite3.connect('/data/finance.db')
    cur = conn.cursor()

    # Доходы
    cur.execute("SELECT title, amount, date FROM incomes WHERE user_id = ?", (user_id,))
    incomes = cur.fetchall()
    total_income = sum(row[1] for row in incomes)

    # Траты
    cur.execute("SELECT title, category, amount, important, date FROM expenses WHERE user_id = ?", (user_id,))
    expenses = cur.fetchall()
    total_expense = sum(row[2] for row in expenses)

    # Последние 5 трат
    cur.execute("SELECT title, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT 5", (user_id,))
    latest_expenses = cur.fetchall()

    # Суммы по категориям
    cur.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
    """, (user_id,))
    category_totals = cur.fetchall()

    conn.close()

    return jsonify({
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "latest_expenses": latest_expenses,
        "category_totals": category_totals,
        "incomes": incomes,
        "expenses": expenses
    })

@app.route('/api/clear', methods=['POST'])
def clear_data():
    conn = sqlite3.connect('/data/finance.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE user_id = 1")
    cur.execute("DELETE FROM incomes WHERE user_id = 1")
    conn.commit()
    conn.close()
    return jsonify({"message": "База очищена"})
if __name__ == '__main__':
    app.run(debug=True, port=8080)

