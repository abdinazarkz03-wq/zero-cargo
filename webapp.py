import os
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
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <title>Регистрация</title>
            <style>
                body { background: #000; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
                .card { width: 90%; text-align: center; }
                h2 { color: #f3d01a; text-transform: uppercase; }
                input { width: 100%; padding: 15px; margin: 10px 0; border-radius: 10px; border: 1px solid #333; background: #111; color: #fff; box-sizing: border-box; font-size: 16px; }
                button { width: 100%; padding: 15px; background: #f3d01a; border: none; border-radius: 10px; font-weight: bold; font-size: 16px; cursor: pointer; color: #000; margin-top: 10px; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>РЕГИСТРАЦИЯ</h2>
                <input id="n" type="text" placeholder="ФИО">
                <input id="p" type="tel" placeholder="Номер телефона">
                <button id="btn" onclick="sendData()">ПОЛУЧИТЬ КОД</button>
            </div>
            <script src="https://telegram.org/js/telegram-web-app.js"></script>
            <script>
                const tg = window.Telegram.WebApp;
                tg.expand();
                
                async function sendData() {
                    const name = document.getElementById('n').value;
                    const phone = document.getElementById('p').value;
                    const btn = document.getElementById('btn');
                    
                    if(!name || !phone) { alert('Заполните поля!'); return; }
                    
                    btn.disabled = true;
                    btn.innerText = 'ОТПРАВКА...';

                    try {
                        // ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ПУТИ
                        const response = await fetch('/api/register', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                telegram_id: String(tg.initDataUnsafe.user.id),
                                full_name: name,
                                phone: phone
                            })
                        });
                        
                        const data = await response.json();
                        if(data.success) {
                            alert('УСПЕХ! Ваш код: ' + data.client_code);
                            tg.close();
                        } else {
                            alert('Ошибка: ' + data.error);
                            btn.disabled = false;
                        }
                    } catch (e) {
                        alert('СЕРВЕР ОБНОВЛЯЕТСЯ. Нажмите еще раз через 20 секунд.');
                        btn.disabled = false;
                        btn.innerText = 'ПОЛУЧИТЬ КОД';
                    }
                }
            </script>
        </body>
        </html>
    ''')

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    if not data: return jsonify({"success": False, "error": "No data"}), 400
    try:
        code = db.create_user(data['telegram_id'], data['full_name'], data['phone'])
        return jsonify({"success": True, "client_code": code})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
