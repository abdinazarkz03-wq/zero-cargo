from flask import Flask, request, jsonify, render_template_string
from database import Database
import os
import requests
import pandas as pd

app = Flask(__name__)
db = Database()

# --- ДИЗАЙН: РЕГИСТРАЦИЯ (ZERO CARGO STYLE) ---
REGISTER_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zero Cargo - Регистрация</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, sans-serif; background: #000; color: #fff; }
  .header { padding: 40px 20px; text-align: center; }
  .logo { font-size: 32px; font-weight: 900; letter-spacing: 3px; }
  .logo span { color: #f3d01a; }
  .container { padding: 0 25px; }
  .card { background: #1a1a1a; border-radius: 20px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
  .title { font-size: 22px; font-weight: 700; margin-bottom: 20px; text-align: center; }
  label { display: block; font-size: 13px; color: #888; margin-bottom: 8px; margin-left: 5px; }
  input { width: 100%; padding: 16px; background: #262626; border: 1px solid #333; border-radius: 12px; color: #fff; font-size: 16px; margin-bottom: 20px; outline: none; }
  input:focus { border-color: #f3d01a; }
  .btn { width: 100%; padding: 18px; background: #fff; color: #000; border: none; border-radius: 12px; font-size: 17px; font-weight: 800; cursor: pointer; }
  .success { display: none; text-align: center; }
  .code-box { background: #f3d01a; color: #000; padding: 20px; border-radius: 15px; font-size: 28px; font-weight: 900; margin: 20px 0; }
</style>
</head>
<body>
  <div class="header"><div class="logo">ZERO<span>CARGO</span></div></div>
  <div class="container">
    <div class="card" id="form-section">
      <div class="title">Регистрация клиента</div>
      <label>ВАШЕ ФИО</label><input type="text" id="fullname" placeholder="Иван Иванов">
      <label>НОМЕР ТЕЛЕФОНА</label><input type="tel" id="phone" placeholder="+996 --- -- -- --">
      <button class="btn" onclick="register()">ПОЛУЧИТЬ КОД</button>
    </div>
    <div class="card success" id="success-section">
      <div style="font-size: 50px;">✅</div>
      <div class="title">Вы успешно зарегистрированы!</div>
      <p style="color: #888;">Ваш личный код для заказов:</p>
      <div class="code-box" id="show-code"></div>
      <p style="font-size: 14px; color: #f3d01a;">Сохраните его и указывайте в адресе!</p>
    </div>
  </div>
<script>
const tg = window.Telegram.WebApp;
tg.ready(); tg.expand();
async function register() {
  const name = document.getElementById('fullname').value;
  const phone = document.getElementById('phone').value;
  if(!name || !phone) { alert('Заполните все поля!'); return; }
  const res = await fetch('/api/register', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({telegram_id: tg.initDataUnsafe?.user?.id || 0, full_name: name, phone})
  });
  const data = await res.json();
  if(data.success) {
    document.getElementById('form-section').style.display = 'none';
    document.getElementById('success-section').style.display = 'block';
    document.getElementById('show-code').textContent = data.client_code;
    setTimeout(() => tg.close(), 7000);
  }
}
</script>
</body>
</html>
"""

# --- ДИЗАЙН: АДМИН-ПАНЕЛЬ (ZERO CARGO ADMIN) ---
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body { font-family: sans-serif; background: #0b0b0b; color: #fff; padding: 20px; }
  .card { background: #1a1a1a; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #333; }
  .btn { background: #f3d01a; color: #000; padding: 12px; border: none; border-radius: 8px; font-weight: bold; width: 100%; cursor: pointer; }
  input { width: 100%; padding: 10px; margin: 10px 0; background: #262626; border: 1px solid #333; color: #fff; border-radius: 8px; }
  table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 12px; }
  th, td { padding: 10px; border-bottom: 1px solid #333; text-align: left; }
  th { color: #888; }
</style>
</head>
<body>
    <h2>ZERO CARGO ADMIN</h2>
    <div class="card">
        <h3>📤 Массовая загрузка (Excel)</h3>
        <p style="font-size: 11px; color: #888; margin-bottom: 10px;">Формат: Код клиента | Трек-номер | Описание | Вес</p>
        <input type="file" id="excel_file" accept=".xlsx, .xls">
        <button class="btn" onclick="uploadExcel()">ЗАГРУЗИТЬ И ОПОВЕСТИТЬ</button>
    </div>
    <div class="card">
        <h3>👥 База клиентов</h3>
        <table>
            <thead><tr><th>Код</th><th>ФИО</th><th>Телефон</th></tr></thead>
            <tbody id="users"></tbody>
        </table>
    </div>
<script>
async function load() {
    const r = await fetch('/api/admin/users');
    const data = await r.json();
    document.getElementById('users').innerHTML = data.map(u => 
        `<tr><td style="color:#f3d01a; font-weight:bold;">${u.client_code}</td><td>${u.full_name}</td><td>${u.phone}</td></tr>`
    ).join('');
}
async function uploadExcel() {
    const file = document.getElementById('excel_file').files[0];
    if(!file) return alert('Выберите файл!');
    const formData = new FormData(); formData.append('file', file);
    const r = await fetch('/api/admin/upload_excel', {method: 'POST', body: formData});
    if(r.ok) { alert('Успешно! Все клиенты получили уведомления.'); load(); }
    else { alert('Ошибка при загрузке'); }
}
load();
</script>
</body>
</html>
"""

# --- МАРШРУТЫ ПРИЛОЖЕНИЯ ---

@app.route("/")
def index():
    return "Zero Cargo Web Service is Running"

@app.route("/register")
def register_page():
    return render_template_string(REGISTER_HTML)

@app.route("/admin")
def admin_page():
    return render_template_string(ADMIN_HTML)

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    # Вызываем метод из твоей новой database.py
    code = db.create_user(data['telegram_id'], data['full_name'], data['phone'])
    return jsonify({"success": True, "client_code": code})

@app.route("/api/admin/users")
def api_users():
    return jsonify(db.get_all_users())

@app.route("/api/admin/upload_excel", methods=["POST"])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file"}), 400
    
    file = request.files['file']
    df = pd.read_excel(file)
    bot_token = os.getenv("BOT_TOKEN")
    
    for _, row in df.iterrows():
        # Колонки в Excel: [0] Код клиента, [1] Трек-номер, [2] Описание, [3] Вес
        try:
            code = str(row[0]).strip()
            track = str(row[1]).strip()
            desc = str(row[2]).strip()
            weight = float(row[3])
            
            # Сохраняем в базу (метод из твоей database.py)
            success = db.add_parcel(code, track, desc, weight, status="Прибыло на склад")
            
            if success:
                # Находим пользователя для отправки сообщения (метод, который мы добавили в database.py)
                user = db.get_user_by_code(code)
                if user:
                    msg = (f"📦 **Новая посылка добавлена!**\\n\\n"
                           f"🔢 Трек: `{track}`\\n"
                           f"⚖️ Вес: {weight} кг\\n"
                           f"📝 {desc}\\n\\n"
                           f"Вы можете отследить статус в разделе 'Мои посылки'.")
                    
                    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", 
                                 json={"chat_id": user['telegram_id'], "text": msg, "parse_mode": "Markdown"})
        except Exception as e:
            print(f"Ошибка при обработке строки Excel: {e}")
            continue

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
