import os
import requests
import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from database import Database

app = Flask(__name__)
db = Database()

@app.route("/")
def home(): return "Бот работает!"

# Страница регистрации
@app.route("/register")
def register_page():
    return render_template_string('''
        <body style="background:#000;color:#fff;text-align:center;padding:20px;font-family:sans-serif;">
            <h2 style="color:#f3d01a;">РЕГИСТРАЦИЯ</h2>
            <input id="n" placeholder="ФИО" style="width:80%;padding:10px;margin:10px 0;border-radius:8px;">
            <input id="p" placeholder="Телефон" style="width:80%;padding:10px;margin:10px 0;border-radius:8px;">
            <button onclick="reg()" style="width:80%;padding:12px;background:#f3d01a;border:none;border-radius:8px;font-weight:bold;">ОТПРАВИТЬ</button>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>
                const tg = window.Telegram.WebApp;
                async function reg(){
                    const r = await fetch('/api/register', {
                        method:'POST', headers:{'Content-Type':'application/json'},
                        body: JSON.stringify({telegram_id:tg.initDataUnsafe.user.id, full_name:document.getElementById('n').value, phone:document.getElementById('p').value})
                    });
                    const d = await r.json();
                    if(d.success) { alert('Регистрация прошла! Ваш код: ' + d.client_code); tg.close(); }
                }
            </script>
        </body>
    ''')

# Страница "Мои посылки"
@app.route("/parcels")
def parcels_page():
    return render_template_string('''
        <body style="background:#000;color:#fff;padding:20px;font-family:sans-serif;">
            <h3 style="color:#f3d01a;">📦 Мои посылки</h3>
            <div id="l">Загрузка...</div>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>
                const tg = window.Telegram.WebApp;
                async function load(){
                    const r = await fetch(`/api/user/parcels?tid=${tg.initDataUnsafe.user.id}`);
                    const d = await r.json();
                    document.getElementById('l').innerHTML = d.map(p => `
                        <div style="border:1px solid #333;padding:10px;margin-bottom:10px;border-radius:8px;">
                            <b>Трек:</b> ${p.track_number}<br><b>Вес:</b> ${p.weight} кг<br>
                            <b style="color:#f3d01a">Статус: ${p.status}</b>
                        </div>
                    `).join('') || "Посылок пока нет";
                }
                load();
            </script>
        </body>
    ''')

# Админ-панель
@app.route("/admin")
def admin_page():
    return render_template_string('''
        <body style="background:#000;color:#fff;text-align:center;padding:20px;font-family:sans-serif;">
            <h3 style="color:#f3d01a;">Админ-панель</h3>
            <input type="file" id="f" style="margin:20px 0;">
            <button onclick="up()" style="width:80%;padding:12px;background:#f3d01a;border:none;border-radius:8px;font-weight:bold;">ЗАГРУЗИТЬ EXCEL</button>
            <script>
                async function up(){
                    const file = document.getElementById('f').files[0];
                    const formData = new FormData(); formData.append('file', file);
                    const r = await fetch('/api/admin/upload_excel', {method:'POST', body:formData});
                    if(r.ok) alert('Данные успешно загружены!');
                }
            </script>
        </body>
    ''')

# --- API ЭНДПОИНТЫ ---
@app.route("/api/register", methods=["POST"])
def api_reg():
    data = request.json
    code = db.create_user(data['telegram_id'], data['full_name'], data['phone'])
    return jsonify({"success":True, "client_code":code})

@app.route("/api/user/parcels")
def api_parcels():
    tid = request.args.get('tid')
    return jsonify(db.get_user_parcels(tid))

@app.route("/api/admin/upload_excel", methods=["POST"])
def upload_excel():
    file = request.files['file']
    df = pd.read_excel(file)
    token = os.getenv("BOT_TOKEN")
    for _, row in df.iterrows():
        code, track, desc, weight = str(row[0]), str(row[1]), str(row[2]), float(row[3])
        if db.add_parcel(code, track, desc, weight, status="На складе"):
            user = db.get_user_by_code(code)
            if user:
                msg = f"📦 **Посылка на складе!**\\n\\n🔢 Трек: `{track}`\\n⚖️ Вес: {weight} кг"
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":user['telegram_id'], "text":msg, "parse_mode":"Markdown"})
    return jsonify({"success":True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
