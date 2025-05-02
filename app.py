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

@app.route('/api/debug', methods=['GET'])
def debug_data():
    conn = sqlite3.connect("/data/finance.db")  # или './finance.db' для локального
    conn.row_factory = sqlite3.Row  # Позволяет получить названия колонок
    cur = conn.cursor()

    cur.execute("SELECT * FROM expenses")
    expenses = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT * FROM incomes")
    incomes = [dict(row) for row in cur.fetchall()]

    conn.close()
    return jsonify({
        "expenses": expenses,
        "incomes": incomes,
        "count": {
            "expenses": len(expenses),
            "incomes": len(incomes)
        }
    })


@app.route('/api/edit_row', methods=['POST'])
def edit_row():
    data = request.json
    table = data.get("table")
    row_id = data.get("id")
    fields = data.get("fields", {})

    if table not in ["expenses", "incomes"] or not row_id or not fields:
        return jsonify({"error": "Invalid input"}), 400

    set_clause = ", ".join([f"{key} = ?" for key in fields.keys()])
    values = list(fields.values()) + [row_id]

    conn = sqlite3.connect("/data/finance.db")
    cur = conn.cursor()
    cur.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", values)
    conn.commit()
    conn.close()

    return jsonify({"message": "Запись обновлена"})


@app.route("/api/income_plan", methods=["POST"])
def income_plan():
    data = request.json
    income = int(data["income"])
    user_id = int(data.get("user_id", 1))

    plan = {
        "essentials": round(income * 0.4),
        "investments": round(income * 0.35),
        "goals": round(income * 0.1),
        "safety": round(income * 0.1),
        "fun": round(income * 0.05)
    }

    conn = sqlite3.connect("/data/finance.db")
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO income_plan (user_id, income, essentials, investments, goals, safety, fun, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime("now"))
    ''', (user_id, income, plan["essentials"], plan["investments"], plan["goals"], plan["safety"], plan["fun"]))
    conn.commit()
    conn.close()

    return jsonify({ "message": "План добавлен", "plan": plan })


@app.route("/api/get_income_plan", methods=["GET"])
def get_income_plan():
    user_id = request.args.get("user_id", 1)
    conn = sqlite3.connect("/data/finance.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT income, essentials, investments, goals, safety, fun, date
        FROM income_plan WHERE user_id = ? ORDER BY date DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()

    return jsonify({ "plans": rows })

if __name__ == '__main__':
    def init_income_plan_table():
        conn = sqlite3.connect("/data/finance.db")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS income_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                income INTEGER,
                essentials INTEGER,
                investments INTEGER,
                goals INTEGER,
                safety INTEGER,
                fun INTEGER,
                date TEXT
            )
        """)
        conn.commit()
        conn.close()

    init_income_plan_table()
    app.run(debug=True, port=8080)

