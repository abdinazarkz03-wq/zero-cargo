import os
import requests
import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from database import Database

app = Flask(__name__)
db = Database()

# Главная страница для проверки работы
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
            input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 10px; border: 1px solid #333; background: #111; color: #fff; font-size: 16px; }
            button { width: 90%; padding: 15px; background: #f3d01a; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; margin-top: 10px; color: #000; }
        </style>
        </head>
        <body>
            <h2 style="color:#f3d01a;">РЕГИСТРАЦИЯ</h2>
            <p>Введите данные для получения личного кода</p>
            <input id="n" type="text" placeholder="ФИО (Иван Иванов)">
            <input id="p" type="tel" placeholder="Номер телефона">
            <button onclick="reg()">ЗАРЕГИСТРИРОВАТЬСЯ</button>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>
                const tg = window.Telegram.WebApp;
                tg.expand();
                async function reg(){
                    const name = document.getElementById('n').value;
                    const phone = document.getElementById('p').value;
                    if(!name || !phone) return alert('Пожалуйста, заполните все поля');
                    
                    try {
                        const r = await fetch('/api/register', {
                            method:'POST', headers:{'Content-Type':'application/json'},
                            body: JSON.stringify({telegram_id: tg.initDataUnsafe.user.id, full_name: name, phone: phone})
                        });
                        const d = await r.json();
                        if(d.success) { 
                            alert('Готово! Ваш личный код: ' + d.client_code); 
                            tg.close(); 
                        }
                    } catch(e) { alert('Ошибка связи с сервером'); }
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
            .track { font-family: monospace; color: #aaa; font-size: 1.1em; }
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
                    if(d.length === 0) {
                        document.getElementById('list').innerHTML = "<p style='text-align:center;color:#444;'>Посылок пока нет</p>";
                        return;
                    }
                    document.getElementById('list').innerHTML = d.map(p => `
                        <div class="p-card">
                            <div class="track">${p.track_number}</div>
                            <div style="margin: 5px 0;">⚖️ ${p.weight} кг</div>
                            <div class="status">📍 ${p.status}</div>
                        </div>
                    `).join('');
                }
                load();
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
    if 'file' not in request.files: return jsonify({"error": "No file"}), 400
    file = request.files['file']
    df = pd.read_excel(file)
    token = os.getenv("BOT_TOKEN")
    
    for _, row in df.iterrows():
        # Читаем: Код, Трек, Описание, Вес
        code = str(row.iloc[0]).strip()
        track = str(row.iloc[1]).strip()
        desc = str(row.iloc[2])
        try:
            weight = float(row.iloc[3])
        except: weight = 0.0
        
        if db.add_parcel(code, track, desc, weight, status="На складе"):
            user = db.get_user_by_code(code)
            if user:
                msg = f"📦 **Посылка на складе!**\\n\\n🔢 Трек: `{track}`\\n⚖️ Вес: {weight} кг"
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                             json={"chat_id": user['telegram_id'], "text": msg, "parse_mode": "Markdown"})
    return jsonify({"success": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
