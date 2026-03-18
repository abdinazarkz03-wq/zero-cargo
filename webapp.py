import os
import requests
import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from database import Database

app = Flask(__name__)
db = Database()

# Главная страница (чтобы проверить, живой ли сайт)
@app.route("/")
def home():
    return "✅ Сервер ZERO CARGO запущен и работает!"

# --- СТРАНИЦА РЕГИСТРАЦИИ ---
@app.route("/register")
def register_page():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { background: #000; color: #fff; text-align: center; font-family: sans-serif; padding: 20px; }
            input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 10px; border: 1px solid #333; background: #111; color: #fff; }
            button { width: 90%; padding: 15px; background: #f3d01a; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        </style>
        </head>
        <body>
            <h2 style="color:#f3d01a;">РЕГИСТРАЦИЯ</h2>
            <p>Введите ваши данные для получения кода</p>
            <input id="n" type="text" placeholder="ФИО (например: Иван Иванов)">
            <input id="p" type="tel" placeholder="Номер телефона">
            <button onclick="reg()">ЗАРЕГИСТРИРОВАТЬСЯ</button>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>
                const tg = window.Telegram.WebApp;
                tg.expand();
                async function reg(){
                    const name = document.getElementById('n').value;
                    const phone = document.getElementById('p').value;
                    if(!name || !phone) return alert('Пожалуйста, заполни все поля');
                    const r = await fetch('/api/register', {
                        method:'POST', headers:{'Content-Type':'application/json'},
                        body: JSON.stringify({telegram_id: tg.initDataUnsafe.user.id, full_name: name, phone: phone})
                    });
                    const d = await r.json();
                    if(d.success) { alert('Готово! Ваш личный код: ' + d.client_code); tg.close(); }
                }
            </script>
        </body>
        </html>
    ''')

# --- СТРАНИЦА МОИ ПОСЫЛКИ ---
@app.route("/parcels")
def parcels_page():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { background: #000; color: #fff; font-family: sans-serif; padding: 15px; }
            .p-card { background: #111; border: 1px solid #222; padding: 15px; border-radius: 12px; margin-bottom: 12px; }
            .status { color: #f3d01a; font-weight: bold; font-size: 0.9em; }
            .track { font-family: monospace; color: #aaa; }
        </style>
        </head>
        <body>
            <h3 style="text-align:center;">📦 МОИ ПОСЫЛКИ</h3>
            <div id="list">Загрузка...</div>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>
                const tg = window.Telegram.WebApp;
                async function load(){
                    const r = await fetch(`/api/user/parcels?tid=${tg.initDataUnsafe.user.id}`);
                    const d = await r.json();
                    document.getElementById('list').innerHTML = d.map(p => `
                        <div class="p-card">
                            <div class="track">${p.track_number}</div>
                            <div style="margin: 5px 0;">⚖️ ${p.weight} кг</div>
                            <div class="status">📍 ${p.status}</div>
                        </div>
                    `).join('') || "<p style='text-align:center;color:#444;'>Посылок пока нет</p>";
                }
                load();
            </script>
        </body>
        </html>
    ''')

# --- СТРАНИЦА АДМИНКИ ---
@app.route("/admin")
def admin_page():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8">
        <style>
            body { background: #000; color: #fff; text-align: center; font-family: sans-serif; padding: 30px; }
            .box { border: 2px dashed #333; padding: 40px; border-radius: 20px; }
            button { background: #f3d01a; padding: 15px 30px; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; }
        </style>
        </head>
        <body>
            <h3>УПРАВЛЕНИЕ ЗАКАЗАМИ</h3>
            <div class="box">
                <input type="file" id="f" style="margin-bottom:20px;"><br>
                <button onclick="up()">ЗАГРУЗИТЬ EXCEL</button>
            </div>
            <script>
                async function up(){
                    const file = document.getElementById('f').files[0];
                    if(!file) return alert('Сначала выбери файл!');
                    const formData = new FormData(); formData.append('file', file);
                    const r = await fetch('/api/admin/upload_excel', {method: 'POST', body: formData});
                    if(r.ok) alert('Успешно! Клиенты получили уведомления.');
                    else alert('Ошибка при загрузке');
                }
            </script>
        </body>
        </html>
    ''')

# --- API ЭНДПОИНТЫ ---
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    code = db.create_user(data['telegram_id'], data['full_name'], data['phone'])
    return jsonify({"success": True, "client_code": code})

@app.route("/api/user/parcels")
def api_user_parcels():
    tid = request.args.get('tid')
    return jsonify(db.get_user_parcels(tid))

@app.route("/api/admin/upload_excel", methods=["POST"])
def upload_excel():
    file = request.files['file']
    df = pd.read_excel(file)
    token = os.getenv("BOT_TOKEN")
    for _, row in df.iterrows():
        # Берем данные из колонок: Код клиента, Трек, Описание, Вес
        code, track, desc, weight = str(row[0]), str(row[1]), str(row[2]), float(row[3])
        if db.add_parcel(code, track, desc, weight, status="На складе"):
            user = db.get_user_by_code(code)
            if user:
                msg = f"📦 **Посылка на складе!**\\n\\n🔢 Трек: `{track}`\\n⚖️ Вес: {weight} кг"
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": user['telegram_id'], "text": msg, "parse_mode": "Markdown"})
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
