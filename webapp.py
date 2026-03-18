from flask import Flask, request, jsonify, render_template_string
from database import Database
import os, requests
import pandas as pd

app = Flask(__name__)
db = Database()

# Форма регистрации
REGISTER_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body { font-family: sans-serif; background: #000; color: #fff; text-align: center; padding: 20px; }
  .card { background: #1a1a1a; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
  input { width: 100%; padding: 15px; margin: 10px 0; background: #262626; border: 1px solid #333; color: #fff; border-radius: 12px; }
  .btn { width: 100%; padding: 15px; background: #f3d01a; color: #000; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; }
</style>
</head>
<body>
    <div class="card" id="reg">
        <h2>ZERO CARGO</h2>
        <input type="text" id="name" placeholder="ФИО">
        <input type="tel" id="phone" placeholder="Телефон">
        <button class="btn" onclick="reg()">ЗАРЕГИСТРИРОВАТЬСЯ</button>
    </div>
    <script>
        const tg = window.Telegram.WebApp;
        async function reg() {
            const res = await fetch('/api/register', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({telegram_id: tg.initDataUnsafe.user.id, full_name: document.getElementById('name').value, phone: document.getElementById('phone').value})
            });
            const data = await res.json();
            if(data.success) { alert('Ваш код: ' + data.client_code); tg.close(); }
        }
    </script>
</body>
</html>
"""

# Админка
ADMIN_HTML = """
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
body { background: #0b0b0b; color: #fff; font-family: sans-serif; padding: 20px; }
.btn { background: #f3d01a; color: #000; padding: 10px; border-radius: 8px; cursor: pointer; width: 100%; border: none; }
input { background: #222; color: #fff; border: 1px solid #444; padding: 10px; width: 100%; margin: 10px 0; }
</style></head>
<body>
    <h3>Админ-панель ZERO CARGO</h3>
    <input type="file" id="file">
    <button class="btn" onclick="upload()">ЗАГРУЗИТЬ EXCEL</button>
    <script>
    async function upload() {
        const file = document.getElementById('file').files[0];
        const formData = new FormData(); formData.append('file', file);
        const r = await fetch('/api/admin/upload_excel', {method: 'POST', body: formData});
        if(r.ok) alert('Успешно отправлено!');
    }
    </script>
</body></html>
"""

@app.route("/register")
def register_page(): return render_template_string(REGISTER_HTML)

@app.route("/admin")
def admin_page(): return render_template_string(ADMIN_HTML)

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    code = db.create_user(data['telegram_id'], data['full_name'], data['phone'])
    return jsonify({"success": True, "client_code": code})

@app.route("/api/admin/users")
def api_users(): return jsonify(db.get_all_users())

@app.route("/api/admin/upload_excel", methods=["POST"])
def upload_excel():
    file = request.files['file']
    df = pd.read_excel(file)
    bot_token = os.getenv("BOT_TOKEN")
    for _, row in df.iterrows():
        code, track, desc, weight = str(row[0]), str(row[1]), str(row[2]), float(row[3])
        if db.add_parcel(code, track, desc, weight, status="На складе"):
            user = db.get_user_by_code(code)
            if user:
                msg = f"📦 **Посылка на складе!**\\n\\n🔢 Трек: `{track}`\\n⚖️ Вес: {weight} кг"
                requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={"chat_id": user['telegram_id'], "text": msg, "parse_mode": "Markdown"})
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
