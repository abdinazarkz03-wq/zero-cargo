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
        <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { background: #000; color: #fff; text-align: center; font-family: sans-serif; padding: 20px; }
            input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 10px; border: 1px solid #333; background: #111; color: #fff; font-size: 16px; }
            button { width: 90%; padding: 15px; background: #f3d01a; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; color: #000; }
        </style>
        </head>
        <body>
            <h2 style="color:#f3d01a;">РЕГИСТРАЦИЯ</h2>
            <input id="n" type="text" placeholder="ФИО">
            <input id="p" type="tel" placeholder="Номер телефона">
            <button onclick="reg()">ПОЛУЧИТЬ КОД</button>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>
                const tg = window.Telegram.WebApp;
                async function reg(){
                    const name = document.getElementById('n').value;
                    const phone = document.getElementById('p').value;
                    if(!name || !phone) return alert('Заполните поля');
                    const r = await fetch('/api/register', {
                        method:'POST', headers:{'Content-Type':'application/json'},
                        body: JSON.stringify({telegram_id: tg.initDataUnsafe.user.id, full_name: name, phone: phone})
                    });
                    const d = await r.json();
                    if(d.success) { alert('Ваш код: ' + d.client_code); tg.close(); }
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
        <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { background: #000; color: #fff; font-family: sans-serif; padding: 15px; }
            .p-card { background: #111; border: 1px solid #222; padding: 15px; border-radius: 12px; margin-bottom: 10px; }
            .status { color: #f3d01a; font-weight: bold; }
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
                            <div>Track: ${p.track_number}</div>
                            <div class="status">Статус: ${p.status} | ${p.weight}кг</div>
                        </div>
                    `).join('') || "Посылок нет";
                }
                load();
            </script>
        </body>
        </html>
    ''')

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    code = db.create_user(data['telegram_id'], data['full_name'], data['phone'])
    return jsonify({"success": True, "client_code": code})

@app.route("/api/user/parcels")
def api_user_parcels():
    tid = request.args.get('tid')
    return jsonify(db.get_user_parcels(tid))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
