from flask import Flask, request, jsonify, render_template_string
from database import Database
import os

app = Flask(__name__)
db = Database()

# --- ТВОИ ДИЗАЙНЕРСКИЕ ШАБЛОНЫ (HTML) ---

REGISTER_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zero Cargo - Регистрация</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; min-height: 100vh; }
  .header { background: #000; color: white; padding: 20px; text-align: center; }
  .logo { font-size: 28px; font-weight: 900; letter-spacing: 2px; }
  .logo span { color: #888; }
  .subtitle { font-size: 13px; color: #aaa; margin-top: 4px; }
  .container { padding: 24px 20px; max-width: 500px; margin: 0 auto; }
  .title { font-size: 22px; font-weight: 700; text-align: center; margin-bottom: 24px; }
  .form-group { margin-bottom: 18px; }
  label { display: block; font-size: 14px; font-weight: 600; color: #333; margin-bottom: 8px; }
  input { width: 100%; padding: 14px 16px; border: 1.5px solid #ddd; border-radius: 12px; font-size: 16px; outline: none; transition: border-color 0.2s; background: white; }
  input:focus { border-color: #000; }
  .btn { width: 100%; padding: 16px; background: #000; color: white; border: none; border-radius: 14px; font-size: 17px; font-weight: 700; cursor: pointer; margin-top: 8px; letter-spacing: 0.5px; }
  .btn:active { opacity: 0.9; transform: scale(0.99); }
  .success { background: #f0fff4; border: 1.5px solid #48bb78; border-radius: 14px; padding: 20px; text-align: center; display: none; }
  .success-icon { font-size: 48px; margin-bottom: 12px; }
  .success h2 { color: #2f855a; font-size: 20px; margin-bottom: 8px; }
  .code-box { background: #000; color: white; border-radius: 12px; padding: 16px; margin: 16px 0; font-size: 24px; font-weight: 900; letter-spacing: 3px; text-align: center; }
  .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; font-size: 14px; }
  .info-row:last-child { border-bottom: none; }
  .info-label { color: #666; }
  .info-value { font-weight: 600; }
  .error { color: #e53e3e; font-size: 13px; margin-top: 6px; display: none; }
</style>
</head>
<body>
<div class="header">
  <div class="logo">ZERO <span>CARGO</span></div>
  <div class="subtitle">Карго Китай 🚛</div>
</div>
<div class="container">
  <div id="form-section">
    <div class="title">📝 Регистрация</div>
    <div class="form-group">
      <label>ФИО</label>
      <input type="text" id="fullname" placeholder="Введите ваше ФИО">
      <div class="error" id="name-error">Введите ФИО</div>
    </div>
    <div class="form-group">
      <label>Номер телефона</label>
      <input type="tel" id="phone" placeholder="+996 XXX XX XX XX">
      <div class="error" id="phone-error">Введите номер телефона</div>
    </div>
    <button class="btn" onclick="register()">Зарегистрироваться</button>
  </div>
  <div class="success" id="success-section">
    <div class="success-icon">✅</div>
    <h2>Регистрация завершена!</h2>
    <div class="code-box" id="show-code">ZC-0000</div>
    <div id="user-info"></div>
    <p style="margin-top:12px;color:#666;font-size:13px;">📞 Менеджер: +996505600542</p>
  </div>
</div>
<script>
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

async function register() {
  const name = document.getElementById('fullname').value.trim();
  const phone = document.getElementById('phone').value.trim();
  if (!name || !phone) { alert('Заполните все поля'); return; }
  
  const user = tg.initDataUnsafe?.user;
  const telegram_id = user?.id || 0;
  const lang = user?.language_code === 'ky' ? 'ky' : 'ru';

  try {
    const resp = await fetch('/api/register', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({telegram_id, full_name: name, phone, language: lang})
    });
    const data = await resp.json();
    if (data.success) {
      document.getElementById('form-section').style.display = 'none';
      document.getElementById('success-section').style.display = 'block';
      document.getElementById('show-code').textContent = data.client_code;
      document.getElementById('user-info').innerHTML = `
        <div class="info-row"><span class="info-label">👤 ФИО</span><span class="info-value">${name}</span></div>
        <div class="info-row"><span class="info-label">📱 Телефон</span><span class="info-value">${phone}</span></div>
      `;
      setTimeout(() => tg.close(), 4000);
    }
  } catch(e) { alert('Ошибка соединения'); }
}
</script>
</body>
</html>
"""

PARCELS_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zero Cargo - Мои посылки</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; }
  .header { background: #000; color: white; padding: 20px; text-align: center; }
  .container { padding: 16px; max-width: 500px; margin: 0 auto; }
  .parcel-card { background: white; border-radius: 14px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 6px rgba(0,0,0,0.08); }
  .status-badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
  .status-pending { background: #fff3cd; color: #856404; }
  .status-ready { background: #d4edda; color: #155724; }
</style>
</head>
<body>
<div class="header"><h1>ZERO CARGO</h1></div>
<div class="container">
  <div id="parcels-list">Загрузка...</div>
</div>
<script>
const tg = window.Telegram.WebApp;
const params = new URLSearchParams(window.location.search);
const userId = params.get('user_id') || tg.initDataUnsafe?.user?.id || 0;

async function load() {
  const r = await fetch('/api/parcels?user_id='+userId);
  const data = await r.json();
  const list = document.getElementById('parcels-list');
  if(!data.parcels.length) { list.innerHTML = '<p>Посылок не найдено</p>'; return; }
  list.innerHTML = data.parcels.map(p => `
    <div class="parcel-card">
      <div style="display:flex; justify-content:space-between">
        <b>📦 ${p.track_number || 'Нет трека'}</b>
        <span class="status-badge">${p.status}</span>
      </div>
      <p style="font-size:13px; margin-top:8px">${p.description || ''} - ${p.weight || 0}кг</p>
    </div>
  `).join('');
}
load();
</script>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zero Cargo - Админ</title>
<style>
  body { font-family: sans-serif; background: #f0f0f0; padding: 20px; }
  .card { background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
  input, select, button { width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #ccc; }
  button { background: #000; color: #fff; font-weight: bold; cursor: pointer; }
</style>
</head>
<body>
  <h2>🔧 Админ-панель</h2>
  <div class="card">
    <h3>Добавить посылку</h3>
    <input type="text" id="code" placeholder="Код (ZC-XXXX)">
    <input type="text" id="track" placeholder="Трек-номер">
    <input type="text" id="desc" placeholder="Описание">
    <input type="number" id="weight" placeholder="Вес">
    <select id="status">
        <option value="pending">Ожидается</option>
        <option value="in_china">В Китае</option>
        <option value="ready">Готов к выдаче</option>
    </select>
    <button onclick="add()">Добавить</button>
  </div>
  <script>
    async function add() {
      const body = {
        client_code: document.getElementById('code').value,
        track_number: document.getElementById('track').value,
        description: document.getElementById('desc').value,
        weight: document.getElementById('weight').value,
        status: document.getElementById('status').value
      };
      const r = await fetch('/api/admin/parcel/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
      });
      const res = await r.json();
      alert(res.success ? 'Успешно' : 'Ошибка: ' + res.error);
    }
  </script>
</body>
</html>
"""

# --- МАРШРУТЫ (ROUTES) ---

@app.route("/")
def index():
    return "<h2>Zero Cargo Bot API</h2><p>Running ✅</p>"

@app.route("/register")
def register_page():
    return render_template_string(REGISTER_HTML)

@app.route("/parcels")
def parcels_page():
    return render_template_string(PARCELS_HTML)

@app.route("/admin")
def admin_page():
    return render_template_string(ADMIN_HTML)

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    telegram_id = data.get("telegram_id")
    full_name = data.get("full_name")
    phone = data.get("phone")
    language = data.get("language", "ru")
    if not telegram_id or not full_name:
        return jsonify({"success": False, "error": "Missing data"})
    code = db.create_user(telegram_id, full_name, phone, language)
    return jsonify({"success": True, "client_code": code})

@app.route("/api/parcels")
def api_parcels():
    user_id = request.args.get("user_id")
    parcels = db.get_user_parcels(int(user_id)) if user_id else []
    return jsonify({"parcels": parcels})

@app.route("/api/admin/parcel/add", methods=["POST"])
def api_add_parcel():
    data = request.json
    success = db.add_parcel(
        data["client_code"], data.get("track_number"),
        data.get("description"), data.get("weight"), data.get("status", "pending")
    )
    if success:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Клиент не найден"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
