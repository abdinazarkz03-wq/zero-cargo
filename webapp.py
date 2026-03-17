from flask import Flask, request, jsonify, render_template_string
import os
import sys
import threading

# ================= Путь к проекту =================
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database  # убедись, что database.py есть и содержит нужные методы

app = Flask(__name__)
db = Database()

# Админский ID
ADMIN_ID = int(os.getenv("ADMIN_ID", "1053328646"))

# ================= HTML =================
REGISTER_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Регистрация</title></head>
<body>
<h2>Регистрация</h2>
<input id="name" placeholder="ФИО"><br><br>
<input id="phone" placeholder="Телефон"><br><br>
<button onclick="reg()">Регистрация</button>

<script>
async function reg(){
    const name = document.getElementById("name").value;
    const phone = document.getElementById("phone").value;

    const res = await fetch("/api/register", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({
            telegram_id: 123,  // <-- здесь реальный telegram_id нужно вставлять из бота
            full_name: name,
            phone: phone
        })
    });

    const data = await res.json();
    alert(JSON.stringify(data));
}
</script>
</body></html>"""

# ================= ROUTES =================
@app.route("/")
def index():
    return "<h2>ZERO CARGO ✅</h2>"

@app.route("/register")
def register_page():
    return render_template_string(REGISTER_HTML)

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}

    tid = data.get("telegram_id")
    name = data.get("full_name", "").strip()
    phone = data.get("phone", "").strip()

    if not tid or not name or not phone:
        return jsonify({"success": False, "error": "Заполните все поля"})

    existing = db.get_user(int(tid))
    if existing:
        return jsonify({
            "success": True,
            "code": existing["client_code"],
            "already": True
        })

    try:
        code = db.register_user(int(tid), name, phone)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    if code:
        return jsonify({"success": True, "code": code})

    return jsonify({"success": False, "error": "
