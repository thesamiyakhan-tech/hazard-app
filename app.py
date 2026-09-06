# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime
import os
from database import init_db, get_db_connection
from risk_model import calculate_risk_score, get_risk_category
from nasa_api import get_nasa_power_data

app = Flask(__name__)
app.secret_key = "sih26001_secret_key" # admin login ke liye
CORS(app)

ADMIN_PASSWORD = "check123"
init_db()

os.makedirs("static/uploads", exist_ok=True)

def map_color(category):
    if category == "Red": return "Critical"
    if category == "Orange": return "High"
    if category == "Yellow": return "Moderate"
    return "Low"

@app.route('/')
def home():
    return render_template('map.html')

@app.route('/report')
def report_page():
    return render_template('form.html')

@app.route('/api/nasa/live')
def nasa_live():
    lat = request.args.get('lat', 23.7307)
    lon = request.args.get('long', 92.7173)
    rain = get_nasa_power_data(lat, lon)
    return jsonify({"lat": lat, "long": lon, "nasa_rainfall_mm": rain, "source": "NASA POWER LIVE"})

@app.route('/api/risk/calculate', methods=['POST'])
def calculate_risk():
    data = request.json
    lat = data.get('lat', 23.7307)
    lon = data.get('long', 92.7173)
    slope = float(data.get('slope', 25))
    history = bool(data.get('history', False))

    nasa_rain = get_nasa_power_data(lat, lon)
    if nasa_rain is None:
        nasa_rain = float(data.get('rainfall', 60))

    score = calculate_risk_score(nasa_rain, slope, history)
    category_green_red = get_risk_category(score)
    category_for_map = map_color(category_green_red)

    conn = get_db_connection()
    conn.execute("INSERT INTO risk_scores (lat, long, risk_level, score, rainfall, slope, history, time) VALUES (?,?,?,?,?,?,?,?)",
                 (lat, lon, category_for_map, score, nasa_rain, slope, int(history), str(datetime.now())))
    conn.commit()
    conn.close()

    return jsonify({
        "risk_score": score,
        "risk_category": category_green_red,
        "risk_category_map": category_for_map,
        "inputs_used": {"nasa_rainfall_mm": nasa_rain}
    })

@app.route('/api/risk/scores')
def get_scores():
    conn = get_db_connection()
    rows = conn.execute("SELECT lat, long, risk_level, score, rainfall, slope, history, time FROM risk_scores ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    result = []
    for r in rows:
        result.append({
            "area_name": f"Risk Area {r[0]:.4f}, {r[1]:.4f}",
            "latitude": r[0],
            "longitude": r[1],
            "risk_level": r[2],
            "risk_score": r[3],
            "rainfall_24h_mm": r[4] or 0,
            "rainfall_antecedent_mm": 30,
            "slope_degree": r[5] or 25,
            "road_distance_m": 200,
            "geology_score": 6,
            "landuse_score": 5,
            "drainage_score": 5,
            "data_source": "Live DB + NASA POWER",
            "last_updated": r[7]
        })
    return jsonify(result)

@app.route('/api/reports', methods=['GET', 'POST'])
def reports_handler():
    if request.method == 'GET':
        if session.get('admin_logged_in')!= True:
            return jsonify({"error": "Unauthorized - Please login via /admin"}), 401
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])

    lat = request.form.get('latitude') or request.form.get('lat')
    lon = request.form.get('longitude') or request.form.get('long')
    description = request.form.get('description', '')
    reporter_name = request.form.get('reporter_name', 'Anonymous')
    reporter_type = request.form.get('reporter_type', 'Citizen')
    observation_type = request.form.get('observation_type', '')
    severity = request.form.get('severity', 'Low')

    photo_url = ''
    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename:
            fname = datetime.now().strftime("%Y%m%d%H%M%S_") + file.filename
            fpath = os.path.join("static/uploads", fname)
            file.save(fpath)
            photo_url = fpath

    full_desc = f"[{reporter_type} - {reporter_name}] {observation_type} - {severity} : {description}"

    conn = get_db_connection()
    conn.execute("INSERT INTO reports (lat, long, description, photo_url, status, time) VALUES (?,?,?,?,?,?)",
                 (lat, lon, full_desc, photo_url, 'NEW', str(datetime.now())))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Report saved"})

@app.route('/api/form/submit', methods=['POST'])
def form_submit():
    return reports_handler()

# ===== ADMIN PANEL - SIRF TUMHE DIKHEGA =====
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect('/admin/reports')
        else:
            return "<h3>Wrong Password</h3><a href='/admin'>Try again</a>"
    return """
    <div style="max-width:350px;margin:100px auto;font-family:sans-serif;background:white;padding:24px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,0.1)">
        <h3> Admin Login</h3>
        <p style="font-size:13px;color:#64748b">Only for officials</p>
        <form method="POST">
            <input type="password" name="password" placeholder="Enter admin password" style="width:100%;padding:10px;border:1px solid #ccc;border-radius:6px">
            <button type="submit" style="width:100%;margin-top:12px;background:#1e3a8a;color:white;padding:10px;border:none;border-radius:6px">Login</button>
        </form>
        <a href="/" style="display:block;margin-top:12px;font-size:13px">← Back to Map</a>
    </div>
    """

@app.route('/admin/reports')
def admin_reports_page():
    if session.get('admin_logged_in')!= True:
        return redirect('/admin')
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()
    conn.close()
    html = """
    <head><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <div style="font-family:sans-serif;padding:20px">
    <h2> All Hazard Reports (Private)</h2>
    <a href="/admin/logout" style="color:red">Logout</a> | <a href="/">Back to Map</a><br><br>
    <table border=1 cellpadding=10 style="border-collapse:collapse;width:100%;font-size:13px">
    <tr style="background:#f1f5f9"><th>ID</th><th>Location</th><th>Details</th><th>Photo</th><th>Time</th><th>Status</th></tr>
    """
    for r in rows:
        d = dict(r)
        photo = f"<a href='/{d['photo_url']}' target='_blank'><img src='/{d['photo_url']}' width=100></a>" if d.get('photo_url') else "No photo"
        html += f"<tr><td>{d.get('id')}</td><td>{d.get('lat')}, {d.get('long')}</td><td>{d.get('description')}</td><td>{photo}</td><td>{d.get('time')}</td><td>{d.get('status')}</td></tr>"
    html += "</table></div>"
    return html

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


