import os
from flask import Flask, request, jsonify, render_template_string
from database import Database
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
db = Database()


@app.route("/")
def home():
    return "✅ ZERO CARGO Server is LIVE!"


@app.route("/register")
def register_page():
    return render_template_string('''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Регистрация — ZERO CARGO</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #000; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .card { width: 100%; max-width: 400px; text-align: center; }
        h2 { color: #f3d01a; text-transform: uppercase; font-size: 24px; margin-bottom: 24px; letter-spacing: 2px; }
        input { width: 100%; padding: 15px; margin: 8px 0; border-radius: 10px; border: 1px solid #333; background: #111; color: #fff; font-size: 16px; outline: none; }
        input:focus { border-color: #f3d01a; }
        button { width: 100%; padding: 15px; background: #f3d01a; border: none; border-radius: 10px; font-weight: bold; font-size: 16px; cursor: pointer; color: #000; margin-top: 12px; transition: opacity 0.2s; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .msg { margin-top: 12px; font-size: 14px; color: #f3d01a; min-height: 20px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>⚡ РЕГИСТРАЦИЯ</h2>
        <input id="n" type="text" placeholder="ФИО">
        <input id="p" type="tel" placeholder="Номер телефона">
        <button id="btn" onclick="sendData()">ПОЛУЧИТЬ КОД</button>
        <div class="msg" id="msg"></div>
    </div>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();

        async function sendData() {
            const name = document.getElementById('n').value.trim();
            const phone = document.getElementById('p').value.trim();
            const btn = document.getElementById('btn');
            const msg = document.getElementById('msg');

            if (!name || !phone) { msg.innerText = '⚠️ Заполните все поля!'; return; }

            btn.disabled = true;
            btn.innerText = 'ОТПРАВКА...';
            msg.innerText = '';

            try {
                const userId = tg.initDataUnsafe?.user?.id;
                if (!userId) {
                    msg.innerText = '❌ Откройте через Telegram!';
                    btn.disabled = false;
                    btn.innerText = 'ПОЛУЧИТЬ КОД';
                    return;
                }
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ telegram_id: String(userId), full_name: name, phone: phone })
                });
                const data = await response.json();
                if (data.success) {
                    msg.innerText = '✅ Ваш код: ' + data.client_code;
                    setTimeout(() => tg.close(), 2000);
                } else {
                    msg.innerText = '❌ ' + (data.error || 'Ошибка');
                    btn.disabled = false;
                    btn.innerText = 'ПОЛУЧИТЬ КОД';
                }
            } catch (e) {
                msg.innerText = '⚠️ Сервер обновляется. Попробуйте через 20 сек.';
                btn.disabled = false;
                btn.innerText = 'ПОЛУЧИТЬ КОД';
            }
        }
    </script>
</body>
</html>''')


@app.route("/parcels")
def parcels_page():
    return render_template_string('''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Посылки — ZERO CARGO</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background: #000; color: #fff; font-family: sans-serif; padding: 20px; }
        h2 { color: #f3d01a; text-transform: uppercase; text-align: center; margin-bottom: 20px; letter-spacing: 2px; }
        .parcel { background: #111; border: 1px solid #222; border-radius: 10px; padding: 15px; margin-bottom: 12px; }
        .parcel .track { color: #f3d01a; font-weight: bold; font-size: 14px; }
        .parcel .desc { color: #ccc; font-size: 13px; margin-top: 4px; }
        .parcel .status { color: #aaa; font-size: 12px; margin-top: 6px; }
        .empty { text-align: center; color: #555; margin-top: 40px; font-size: 15px; }
        .loading { text-align: center; color: #f3d01a; margin-top: 40px; }
    </style>
</head>
<body>
    <h2>🚩 МОИ ПОСЫЛКИ</h2>
    <div id="content" class="loading">Загрузка...</div>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();

        async function loadParcels() {
            const userId = tg.initDataUnsafe?.user?.id;
            if (!userId) {
                document.getElementById('content').innerHTML = '<div class="empty">❌ Откройте через Telegram!</div>';
                return;
            }
            try {
                const res = await fetch('/api/parcels?telegram_id=' + userId);
                const data = await res.json();
                const el = document.getElementById('content');
                if (!data.parcels || data.parcels.length === 0) {
                    el.innerHTML = '<div class="empty">📭 Посылок пока нет</div>';
                } else {
                    el.innerHTML = data.parcels.map(p => `
                        <div class="parcel">
                            <div class="track">📦 ${p.tracking_number}</div>
                            <div class="desc">${p.description}</div>
                            <div class="status">🔄 ${p.status} · ${p.created_at}</div>
                        </div>
                    `).join('');
                }
            } catch(e) {
                document.getElementById('content').innerHTML = '<div class="empty">⚠️ Ошибка загрузки</div>';
            }
        }
        loadParcels();
    </script>
</body>
</html>''')


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    if not data:
        return jsonify({"success": False, "error": "Нет данных"}), 400
    tid = data.get('telegram_id', '').strip()
    name = data.get('full_name', '').strip()
    phone = data.get('phone', '').strip()
    if not tid or not name or not phone:
        return jsonify({"success": False, "error": "Заполните все поля"}), 400
    try:
        code = db.create_user(tid, name, phone)
        return jsonify({"success": True, "client_code": code})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/parcels", methods=["GET"])
def api_parcels():
    tid = request.args.get('telegram_id', '').strip()
    if not tid:
        return jsonify({"success": False, "error": "Нет telegram_id"}), 400
    try:
        parcels = db.get_parcels(tid)
        return jsonify({"success": True, "parcels": [dict(p) for p in parcels]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
