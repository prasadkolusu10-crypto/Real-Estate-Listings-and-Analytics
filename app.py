from flask import Flask, render_template, request, send_file, send_from_directory
import mysql.connector
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Prasad@123', 
    'database': 'real_estate'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM Properties")
    total_properties = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM Transactions")
    total_transactions = cursor.fetchone()['total']

    cursor.execute("SELECT AVG(sale_price) AS avg_price FROM Transactions")
    avg_sale_price = cursor.fetchone()['avg_price']
    avg_sale_price = round(avg_sale_price, 2) if avg_sale_price else None

    cursor.close()
    conn.close()

    return render_template('index.html', 
        total_properties=total_properties,
        total_transactions=total_transactions,
        avg_sale_price=avg_sale_price
    )

@app.route('/properties')
def properties():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, a.name AS agent_name 
        FROM Properties p
        JOIN Agents a ON p.agent_id = a.agent_id
    """)
    props = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('properties.html', properties=props)

@app.route('/property/<int:property_id>')
def property_detail(property_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, 
               a.name AS agent_name, 
               a.email AS agent_email, 
               a.phone AS agent_phone
        FROM Properties p
        JOIN Agents a ON p.agent_id = a.agent_id
        WHERE p.property_id = %s
    """, (property_id,))
    prop = cursor.fetchone()
    cursor.close()
    conn.close()

    if not prop:
        return "Property not found", 404

    return render_template('property_detail.html', property=prop)

@app.route('/reports')
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT city, state, AVG(price) AS avg_price, COUNT(*) AS count
        FROM Properties GROUP BY city, state
    """)
    avg_prices = cursor.fetchall()

    cursor.execute("SELECT * FROM HighDemandAreas")
    high_demand = cursor.fetchall()

    cursor.execute("""
        SELECT p.city, t.sale_date, t.sale_price,
        AVG(t.sale_price) OVER (PARTITION BY p.city ORDER BY t.sale_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg
        FROM Transactions t
        JOIN Properties p ON t.property_id = p.property_id
        ORDER BY p.city, t.sale_date
    """)
    trends = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('reports.html', 
        avg_prices=avg_prices, 
        high_demand=high_demand, 
        trends=trends
    )

@app.route('/export/<report>')
def export_csv(report):
    conn = get_db_connection()
    os.makedirs('exports', exist_ok=True)
    filename = f"exports/{report}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    queries = {
        'properties': "SELECT * FROM Properties",
        'transactions': "SELECT * FROM Transactions",
        'avg_prices': """
            SELECT city, state, AVG(price) AS avg_price, COUNT(*) AS count
            FROM Properties GROUP BY city, state
        """,
        'trends': """
            SELECT p.city, t.sale_date, t.sale_price,
            AVG(t.sale_price) OVER (PARTITION BY p.city ORDER BY t.sale_date 
                            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg
            FROM Transactions t JOIN Properties p ON t.property_id = p.property_id
        """,
        'high_demand': "SELECT * FROM HighDemandAreas"
    }

    if report not in queries:
        return "Report not found", 400

    df = pd.read_sql(queries[report], conn)
    df.to_csv(filename, index=False)
    conn.close()

    return send_file(filename, as_attachment=True)

@app.route('/export')
def export():
    return render_template('export.html')

@app.route('/enquiry', methods=['POST'])
def enquiry():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    message = request.form.get('message')

    if not all([name, email, phone, message]):
        return "All fields are required", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Enquiries (name, email, phone, message)
        VALUES (%s, %s, %s, %s)
    """, (name, email, phone, message))

    conn.commit()
    cursor.close()
    conn.close()

    return render_template('enquiry_success.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
