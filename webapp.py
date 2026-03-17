from flask import Flask, request, jsonify, render_template_string
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import Database

app = Flask(__name__)
db = Database()

ADMIN_ID = int(os.getenv("ADMIN_ID", "1053328646"))

# ================= HTML =================

REGISTER_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Регистрация</title></head>
<body>
<h2>Регистрация ZERO CARGO</h2>
<input id="name" placeholder="ФИО"><br><br>
<input id="phone" placeholder="Телефон"><br><br>
<button onclick="reg()">Зарегистрироваться</button>
<p id="msg"></p>

<script>
async function reg(){
    // ✅ Берём telegram_id из URL параметра ?user_id=
    const params = new URLSearchParams(window.location.search);
    const telegram_id = params.get("user_id");

    if (!telegram_id) {
        document.getElementById("msg").innerText = "Ошибка: откройте через Telegram бота";
        return;
    }

    const name = document.getElementById("name").value.trim();
    const phone = document.getElementById("phone").value.trim();

    if (!name || !phone) {
        document.getElementById("msg").innerText = "Заполните все поля";
        return;
    }

    const res = await fetch("/api/register", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ telegram_id, full_name: name, phone })
    });

    const data = await res.json();

    if (data.success) {
        document.getElementById("msg").innerText = "✅ Ваш код: " + data.code;
    } else {
        document.getElementById("msg").innerText = "❌ " + data.error;
    }
}
</script>
</body></html>"""

PARCELS_HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Посылки</title></head>
<body>
<h2>Мои посылки</h2>
<div id="list">Загрузка...</div>
<script>
const params = new URLSearchParams(window.location.search);
const code = params.get("code");

fetch("/api/parcels?code=" + code)
  .then(r => r.json())
  .then(data => {
    if (!data.parcels || data.parcels.length === 0) {
      document.getElementById("list").innerText = "Посылок нет";
      return;
    }
    document.getElementById("list").innerHTML = data.parcels.map(p =>
      `<div style="border:1px solid #ccc;padding:10px;margin:5px">
        <b>${p.track_number}</b><br>
        ${p.description || ""}<br>
        Статус: ${p.status}<br>
        Вес: ${p.weight || "—"} кг
      </div>`
    ).join("");
  });
</script>
</body></html>"""

# ================= ROUTES =================

@app.route("/")
def index():
    return "<h2>ZERO CARGO ✅</h2>"

@app.route("/register")
def register_page():
    return render_template_string(REGISTER_HTML)

@app.route("/parcels")
def parcels_page():
    return render_template_string(PARCELS_HTML)

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
        return jsonify({"success": True, "code": existing["client_code"], "already": True})

    try:
        code = db.register_user(int(tid), name, phone)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

    if code:
        return jsonify({"success": True, "code": code})

    return jsonify({"success": False, "error": "Ошибка регистрации"})

@app.route("/api/user")
def api_user():
    telegram_id = request.args.get("telegram_id")
    if not telegram_id:
        return jsonify({"found": False})

    user = db.get_user(int(telegram_id))
    if user:
        return jsonify({"found": True, **user})
    return jsonify({"found": False})

@app.route("/api/parcels")
def api_parcels():
    code = request.args.get("code")
    if not code:
        return jsonify({"parcels": []})

    parcels = db.get_parcels(code)
    return jsonify({"parcels": parcels})

# ================= ADMIN =================

@app.route("/api/admin/add_parcel", methods=["POST"])
def add_parcel():
    data = request.get_json(silent=True) or {}

    # Простая проверка админа
    if str(data.get("admin_id")) != str(ADMIN_ID):
        return jsonify({"success": False, "error": "Нет доступа"})

    code = data.get("client_code")
    track = data.get("track_number")
    desc = data.get("description", "")
    weight = data.get("weight")
    status = data.get("status", "В обработке")

    if not code or not track:
        return jsonify({"success": False, "error": "code и track_number обязательны"})

    try:
        db.add_parcel(code, track, desc, weight, status)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# ================= ENTRY =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
