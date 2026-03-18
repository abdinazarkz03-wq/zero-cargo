import os
import requests
import pandas as pd
from flask import Flask, request, jsonify, render_template_string
from database import Database

app = Flask(__name__)
db = Database()

@app.route("/")
def home():
    return "✅ ZERO CARGO Server is LIVE!"

@app.route("/register")
def register_page():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Регистрация ZERO CARGO</title>
            <style>
                body { background: #000; color: #fff; text-align: center; font-family: -apple-system, sans-serif; padding: 20px; margin: 0; }
                .container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
                h2 { color: #f3d01a; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 30px; }
                input { 
                    width: 90%; max-width: 300px; padding: 15px; margin: 10px 0; 
                    border-radius: 12px; border: 1px solid #333; background: #111; 
                    color: #fff; font-size: 16px; outline: none;
                }
                input:focus { border-color: #f3d01a; }
                button { 
                    width: 90%; max-width: 300px; padding: 18px; margin-top: 20px;
                    background: #f3d01a; border: none; border-radius: 12px; 
                    font-weight: bold; cursor: pointer; color: #000; 
                    text-transform: uppercase; font-size: 16px;
                }
                button:active { transform: scale(0.98); opacity: 0.9; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Регистрация</h2>
                <input id="n" type="text" placeholder="ФИО (как в паспорте)">
                <input id="p" type="tel" placeholder="Номер телефона">
                <button id="btn" onclick="reg()">Получить код</button>
            </div>

            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>
                const tg = window.Telegram.WebApp;
                tg.expand();
                tg.ready();

                async function reg(){
                    const name = document.getElementById('n').value;
                    const phone = document.getElementById('p').value;
                    const btn = document.getElementById('btn');

                    if(!name || !phone) {
                        alert('Пожалуйста, заполните все поля');
                        return;
                    }

                    btn.disabled = true;
                    btn.innerText = 'Загрузка...';

                    try {
                        const response = await fetch('/api/register', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                telegram_id: tg.initDataUnsafe.user.id,
                                full_name: name,
                                phone: phone
                            })
                        });

                        const data = await response.json();

                        if(data.success) {
                            alert('Регистрация успешна! Ваш личный код: ' + data.client_code);
                            tg.close();
                        } else {
                            alert('Ошибка при регистрации. Попробуйте снова.');
                            btn.disabled = false;
                            btn.innerText = 'Получить код';
                        }
                    } catch (e) {
                        console.error(e);
                        alert('Ошибка связи с сервером. Проверьте интернет.');
                        btn.disabled = false;
                        btn.innerText = 'Получить код';
                    }
                }
            </script>
        </body>
        </html>
    ''')

@app.route("/parcels")
def parcels_page():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { background: #000; color: #fff; font-family: sans-serif; padding: 15px; }
                .p-card { background: #111; border: 1px solid #222; padding: 15px; border-radius: 12px; margin-bottom: 10px; }
                .status { color: #f3d01a; font-weight: bold; }
                h3 { text-align: center; color: #f3d01a; }
            </style>
        </head>
        <body>
            <h3>📦 МОИ ПОСЫЛКИ</h3>
            <div id="list">Загрузка данных...</div>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>
                const tg = window.Telegram.WebApp;
                async function load(){
                    try {
                        const r = await fetch(`/api/user/parcels?tid=${tg.initDataUnsafe.user.id}`);
                        const d = await r.json();
                        if (d.length === 0) {
                            document.getElementById('list').innerHTML = '<p style="text-align:center;">У вас пока нет посылок</p>';
                            return;
                        }
                        document.getElementById('list').innerHTML = d.map(p => `
                            <div class="p-card">
                                <div><b>Трек:</b> ${p.track_number}</div>
                                <div><b>Описание:</b> ${p.description || 'Нет описания'}</div>
                                <div class="status">Статус: ${p.status} | ${p.weight}кг</div>
                            </div>
                        `).join('');
                    } catch (e) {
                        document.getElementById('list').innerHTML = 'Ошибка загрузки';
                    }
                }
                load();
            </script>
        </body>
        </html>
    ''')

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    if not data or 'telegram_id' not in data:
        return jsonify({"success": False, "error": "No data"}), 400
    code = db.create_user(data['telegram_id'], data['full_name'], data['phone'])
    return jsonify({"success": True, "client_code": code})

@app.route("/api/user/parcels")
def api_user_parcels():
    tid = request.args.get('tid')
    if not tid:
        return jsonify([])
    return jsonify(db.get_user_parcels(tid))

@app.route("/api/admin/upload_excel", methods=["POST"])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({"success": False}), 400
    file = request.files['file']
    df = pd.read_excel(file)
    token = os.getenv("BOT_TOKEN")
    for _, row in df.iterrows():
        code, track, desc, weight = str(row.iloc[0]).strip(), str(row.iloc[1]).strip(), str(row.iloc[2]), float(row.iloc[3])
        if db.add_parcel(code, track, desc, weight):
            user = db.get_user_by_code(code)
            if user:
                msg = f"📦 Посылка на складе!\\n🔢 Трек: {track}\\n⚖️ Вес: {weight} кг"
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": user['telegram_id'], "text": msg})
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
