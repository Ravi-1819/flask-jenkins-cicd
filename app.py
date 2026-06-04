from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.environ.get('DB_PATH', 'blood_bank.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        mobile TEXT NOT NULL,
        city TEXT NOT NULL,
        blood_group TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/register', methods=['POST'])
def register_donor():
    data = request.get_json()
    name = data.get('name', '').strip()
    mobile = data.get('mobile', '').strip()
    city = data.get('city', '').strip()
    blood_group = data.get('blood_group', '').strip()

    if not all([name, mobile, city, blood_group]):
        return jsonify({'success': False, 'message': 'Sabhi fields bharna zaroori hai!'}), 400

    if not mobile.isdigit() or len(mobile) != 10:
        return jsonify({'success': False, 'message': 'Mobile number 10 digits ka hona chahiye!'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO donors (name, mobile, city, blood_group) VALUES (?, ?, ?, ?)',
              (name, mobile, city.lower(), blood_group))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': f'Shukriya {name}! Aap humari donors list mein add ho gaye. 🙏'})

@app.route('/api/search', methods=['POST'])
def search_donors():
    data = request.get_json()
    city = data.get('city', '').strip().lower()
    blood_group = data.get('blood_group', '').strip()

    if not all([city, blood_group]):
        return jsonify({'success': False, 'message': 'City aur blood group dono bharna zaroori hai!'}), 400

    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT name, mobile, city, blood_group FROM donors WHERE LOWER(city)=? AND blood_group=?',
              (city, blood_group))
    rows = c.fetchall()
    conn.close()

    donors = [{'name': r['name'], 'mobile': r['mobile'], 'city': r['city'].title(), 'blood_group': r['blood_group']} for r in rows]
    return jsonify({'success': True, 'donors': donors, 'count': len(donors)})

@app.route('/api/stats')
def stats():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as total FROM donors')
    total = c.fetchone()['total']
    c.execute('SELECT COUNT(DISTINCT city) as cities FROM donors')
    cities = c.fetchone()['cities']
    c.execute('SELECT blood_group, COUNT(*) as cnt FROM donors GROUP BY blood_group ORDER BY cnt DESC LIMIT 1')
    row = c.fetchone()
    top_group = row['blood_group'] if row else 'N/A'
    conn.close()
    return jsonify({'total_donors': total, 'cities_covered': cities, 'most_common': top_group})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
