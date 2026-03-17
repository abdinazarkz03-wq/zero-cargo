from flask import Flask, request, jsonify, render_template_string
import os
import sys
import threading

# фикс пути
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

app = Flask(__name__)
db = Database()

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
            telegram_id: 123,
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
    data = request.get_json()

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

    code = db.register_user(int(tid), name, phone)

    if code:
        return jsonify({"success": True, "code": code})

    return jsonify({"success": False, "error": "Ошибка регистрации"})


# ================= ADMIN =================

def check_admin(data):
    return str(data.get("admin_id")) == str(ADMIN_ID)


@app.route("/api/admin/add-parcel", methods=["POST"])
def admin_add_parcel():
    data = request.get_json()

    if not check_admin(data):
        return jsonify({"error": "Unauthorized"}), 403

    if not db.get_user_by_code(data["client_code"]):
        return jsonify({"success": False, "error": "Клиент не найден"})

    db.add_parcel(
        data["client_code"],
        data["track_number"],
        data.get("description"),
        data.get("weight"),
        data.get("status", "В обработке")
    )

    return jsonify({"success": True})


# ================= BOT =================

def run_bot():
    try:
        from bot import main
        main()
    except Exception as e:
        print("Ошибка запуска бота:", e)


# запускаем бот в фоне
t = threading.Thread(target=run_bot, daemon=True)
t.start()


# ================= START =================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
