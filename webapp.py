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
                button:disabled { background: #555; cursor: not-allowed; }
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

                    // АВТОМАТИЧЕСКИЙ АДРЕС
                    const apiUrl = window.location.origin + '/api/register';

                    try {
                        const response = await fetch(apiUrl, {
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
                            alert('Ошибка: ' + (data.error || 'не удалось сохранить данные'));
                            btn.disabled = false;
                            btn.innerText = 'Получить код';
                        }
                    } catch (e) {
                        console.error(e);
                        alert('Ошибка связи с сервером. Попробуйте нажать еще раз через 10 секунд.');
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
                        const apiUrl = window.location.origin + `/api/user/parcels?tid=${tg.initDataUnsafe.user.id}`;
                        const r = await fetch(apiUrl);
                        const d = await r.json();
                        if (d.length === 0) {
                            document.getElementById('list').innerHTML = '<p style="text-align:center;">У вас пока нет посылок</p>';
                            return;
                        }
                        document.getElementById('list').innerHTML = d.map(p => `
                            <div class="p-card">
                                <div><b>Трек:</b> ${p.track_number}</div>
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
    try:
        data = request.json
        if not data or 'telegram_id' not in data:
            return jsonify({"success": False, "error": "Нет данных пользователя"}), 400
        code = db.create_user(data['telegram_id'], data['full_name'], data['phone'])
        return jsonify({"success": True, "client_code": code})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/user/parcels")
def api_user_parcels():
    tid = request.args.get('tid')
    if not tid:
        return jsonify([])
    return jsonify(db.get_user_parcels(tid))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
