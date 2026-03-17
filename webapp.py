from flask import Flask, request, jsonify, render_template_string, send_file
import os
import sys
import logging
from datetime import datetime
import qrcode
from io import BytesIO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import Database

app = Flask(__name__)
db = Database()

ADMIN_ID = int(os.getenv("ADMIN_ID", "1053328646"))

REGISTER_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Регистрация ZERO CARGO</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 400px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h2 { text-align: center; color: #333; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #45a049; }
        .success { color: green; text-align: center; font-weight: bold; }
        .error { color: red; text-align: center; }
        .qr-code { text-align: center; margin: 20px 0; }
        .qr-code img { max-width: 200px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📦 Регистрация ZERO CARGO</h2>
        <input id="name" type="text" placeholder="Ваше ФИО" required>
        <input id="phone" type="tel" placeholder="Номер телефона" required>
        <button onclick="register()">Зарегистрироваться</button>
        <p id="message"></p>
        <div id="qrContainer" style="display:none;" class="qr-code"></div>
    </div>

<script>
async function register() {
    const params = new URLSearchParams(window.location.search);
    const telegram_id = params.get("user_id");
    const name = document.getElementById("name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const messageEl = document.getElementById("message");
    const qrContainer = document.getElementById("qrContainer");

    if (!telegram_id) {
        messageEl.className = "error";
        messageEl.innerText = "Ошибка: откройте через Telegram бота";
        return;
    }

    if (!name || !phone) {
        messageEl.className = "error";
        messageEl.innerText = "Заполните все поля";
        return;
    }

    messageEl.innerText = "Отправка...";
    messageEl.className = "";

    try {
        const res = await fetch("/api/register", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ 
                telegram_id: parseInt(telegram_id), 
                full_name: name, 
                phone: phone 
            })
        });

        const data = await res.json();

        if (data.success) {
            messageEl.className = "success";
            messageEl.innerText = "✅ Регистрация успешна! Ваш код: " + data.code;
            
            qrContainer.style.display = "block";
            const qrImg = document.createElement("img");
            qrImg.src = "/api/qrcode/" + data.code;
            qrImg.alt = "QR-код";
            qrContainer.innerHTML = "<p>Ваш QR-код:</p>";
            qrContainer.appendChild(qrImg);
        } else {
            messageEl.className = "error";
            messageEl.innerText = "❌ " + (data.error || "Ошибка регистрации");
        }
    } catch (error) {
        messageEl.className = "error";
        messageEl.innerText = "❌ Ошибка соединения";
    }
}
</script>
</body></html>"""

PARCELS_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Мои посылки</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 20px auto; padding: 20px; background: #f5f5f5; }
        h2 { text-align: center; color: #333; }
        .parcel { background: white; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .track { font-weight: bold; color: #2196F3; font-size: 16px; }
        .status { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; font-weight: bold; margin-top: 5px; }
        .status-delivered { background: #4CAF50; color: white; }
        .status-transit { background: #FFC107; color: black; }
        .status-processing { background: #9E9E9E; color: white; }
        .refresh { text-align: center; margin: 20px 0; }
        button { padding: 10px 20px; background: #2196F3; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 14px; }
        button:hover { background: #1976D2; }
        .empty { text-align: center; color: #666; padding: 40px; background: white; border-radius: 5px; }
        .info { margin: 5px 0; color: #555; }
    </style>
</head>
<body>
    <h2>📦 Мои посылки</h2>
    <div class="refresh">
        <button onclick="loadParcels()">🔄 Обновить</button>
    </div>
    <div id="list">Загрузка...</div>

<script>
const params = new URLSearchParams(window.location.search);
const code = params.get("code");

function getStatusClass(status) {
    status = status.toLowerCase();
    if (status.includes('достав') || status.includes('получ')) return 'status-delivered';
    if (status.includes('пути') || status.includes('транзит')) return 'status-transit';
    return 'status-processing';
}

async function loadParcels() {
    try {
        const res = await fetch("/api/parcels?code=" + encodeURIComponent(code));
        const data = await res.json();
        
        const list = document.getElementById("list");
        
        if (!data.parcels || data.parcels.length === 0) {
            list.innerHTML = '<div class="empty">📭 У вас пока нет посылок</div>';
            return;
        }
        
        list.innerHTML = data.parcels.map(p => {
            const statusClass = getStatusClass(p.status);
            return `
                <div class="parcel">
                    <div class="track">📦 ${p.track_number || 'Номер не указан'}</div>
                    <div><span class="status ${statusClass}">${p.status || 'В обработке'}</span></div>
                    ${p.description ? `<div class="info">📝 ${p.description}</div>` : ''}
                    ${p.weight ? `<div class="info">⚖️ Вес: ${p.weight} кг</div>` : ''}
                    ${p.estimated_delivery ? `<div class="info">📅 Ожидается: ${p.estimated_delivery}</div>` : ''}
                    <div class="info">📅 Добавлена: ${p.created_at ? p.created_at.split(' ')[0] : ''}</div>
                </div>
            `;
        }).join("");
    } catch (error) {
        document.getElementById("list").innerHTML = '<div class="empty">❌ Ошибка загрузки</div>';
    }
}

loadParcels();
setInterval(loadParcels, 30000);
</script>
</body></html>"""

@app.route("/")
def index():
    return "<h2>✅ ZERO CARGO API работает</h2><p><a href='/register'>Регистрация</a> | <a href='/parcels?code=TEST'>Пример посылок</a></p>"

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/register")
def register_page():
    return render_template_string(REGISTER_HTML)

@app.route("/parcels")
def parcels_page():
    return render_template_string(PARCELS_HTML)

@app.route("/api/qrcode/<client_code>")
def generate_qrcode(client_code):
    img = qrcode.make(f"ZERO-CARGO:{client_code}")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route("/api/register", methods=["POST"])
def api_register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Нет данных"})
        
        telegram_id = data.get("telegram_id")
        full_name = data.get("full_name", "").strip()
        phone = data.get("phone", "").strip()
        
        if not telegram_id or not full_name or not phone:
            return jsonify({"success": False, "error": "Заполните все поля"})
        
        existing = db.get_user(int(telegram_id))
        if existing:
            return jsonify({
                "success": True,
                "code": existing["client_code"],
                "already": True
            })
        
        code = db.register_user(int(telegram_id), full_name, phone)
        
        if code:
            return jsonify({"success": True, "code": code})
        else:
            return jsonify({"success": False, "error": "Ошибка регистрации"})
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/user")
def api_user():
    telegram_id = request.args.get("telegram_id")
    if not telegram_id:
        return jsonify({"found": False})
    
    try:
        user = db.get_user(int(telegram_id))
        if user:
            return jsonify({
                "found": True,
                "client_code": user["client_code"],
                "full_name": user["full_name"],
                "phone": user["phone"]
            })
    except Exception as e:
        logger.error(f"Error getting user: {e}")
    
    return jsonify({"found": False})

@app.route("/api/parcels")
def api_parcels():
    code = request.args.get("code")
    if not code:
        return jsonify({"parcels": []})
    
    try:
        parcels = db.get_parcels(code)
        return jsonify({"parcels": parcels})
    except Exception as e:
        logger.error(f"Error getting parcels: {e}")
        return jsonify({"parcels": [], "error": str(e)})

@app.route("/api/admin/add_parcel", methods=["POST"])
def add_parcel():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "Нет данных"})
        
        if str(data.get("admin_id")) != str(ADMIN_ID):
            return jsonify({"success": False, "error": "Нет доступа"})
        
        client_code = data.get("client_code")
        track_number = data.get("track_number")
        description = data.get("description", "")
        weight = data.get("weight")
        status = data.get("status", "В обработке")
        estimated = data.get("estimated_delivery")
        
        if not client_code or not track_number:
            return jsonify({"success": False, "error": "client_code и track_number обязательны"})
        
        user = db.get_user_by_code(client_code)
        if not user:
            return jsonify({"success": False, "error": "Клиент не найден"})
        
        db.add_parcel(client_code, track_number, description, weight, status, estimated)
        
        return jsonify({"success": True})
        
    except Exception as e:
        logger.error(f"Error adding parcel: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/admin/users", methods=["GET"])
def admin_users():
    admin_id = request.args.get("admin_id")
    if str(admin_id) != str(ADMIN_ID):
        return jsonify({"success": False, "error": "Нет доступа"})
    
    try:
        users = db.get_all_users()
        for user in users:
            user.pop("id", None)
        return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
