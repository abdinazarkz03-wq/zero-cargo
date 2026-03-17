from flask import Flask, request, jsonify, render_template_string
import os
import sys
import threading

# Настройка пути к папке с project
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Безопасный импорт Database
try:
    from database import Database
except Exception as e:
    print("Ошибка импорта database:", e)
    Database = None

app = Flask(__name__)

# Инициализация базы
if Database:
    db = Database()
else:
    db = None

# Безопасное получение ADMIN_ID и PORT
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "1053328646"))
except ValueError:
    print("ADMIN_ID должен быть числом. Установлено значение по умолчанию 1053328646")
    ADMIN_ID = 1053328646

try:
    PORT = int(os.getenv("PORT", 5000))
except ValueError:
    print("PORT должен быть числом. Установлено значение по умолчанию 5000")
    PORT = 5000

# ====================== HTML ======================
# Для краткости используем твои строки REGISTER_HTML, PARCELS_HTML, ADMIN_HTML
# Здесь вставляем их без изменений
REGISTER_HTML = """..."""  # вставь свой код REGISTER_HTML
PARCELS_HTML = """..."""   # вставь свой код PARCELS_HTML
ADMIN_HTML = """..."""      # вставь свой код ADMIN_HTML

# ====================== ROUTES ======================
@app.route("/")
def index():
    return "<h2>ZERO CARGO ✅</h2>"

@app.route("/register")
def register_page():
    return render_template_string(REGISTER_HTML)

@app.route("/parcels")
def parcels_page():
    return render_template_string(PARCELS_HTML)

@app.route("/admin")
def admin_page():
    return render_template_string(ADMIN_HTML, admin_id=ADMIN_ID)

# ====================== API ======================
@app.route("/api/register", methods=["POST"])
def api_register():
    if not db:
        return jsonify({"success": False, "error": "Database не доступна"})
    data = request.get_json() or {}
    tid = data.get("telegram_id")
    name = data.get("full_name", "").strip()
    phone = data.get("phone", "").strip()
    if not tid or not name or not phone:
        return jsonify({"success": False, "error": "Заполните все поля"})
    existing = db.get_user(int(tid))
    if existing:
        return jsonify({"success": True, "code": existing["client_code"], "already": True})
    code = db.register_user(int(tid), name, phone)
    if code:
        return jsonify({"success": True, "code": code})
    return jsonify({"success": False, "error": "Ошибка регистрации"})

@app.route("/api/user")
def api_get_user():
    if not db:
        return jsonify({"found": False})
    tid = request.args.get("telegram_id")
    if not tid:
        return jsonify({"found": False})
    user = db.get_user(int(tid))
    if user:
        user["found"] = True
        return jsonify(user)
    return jsonify({"found": False})

@app.route("/api/update-language", methods=["POST"])
def api_update_language():
    if not db:
        return jsonify({"success": False})
    data = request.get_json() or {}
    db.update_language(int(data.get("telegram_id", 0)), data.get("language"))
    return jsonify({"success": True})

@app.route("/api/parcels")
def api_parcels():
    if not db:
        return jsonify({"parcels": []})
    code = request.args.get("code", "")
    return jsonify({"parcels": db.get_parcels_by_code(code)})

@app.route("/api/search-parcel")
def api_search_parcel():
    if not db:
        return jsonify({"parcels": []})
    track = request.args.get("track", "")
    code = request.args.get("code", "")
    results = [p for p in db.search_parcel_by_track(track) if p["client_code"] == code]
    return jsonify({"parcels": results})

# ====================== ADMIN ======================
def check_admin(data):
    return str(data.get("admin_id")) == str(ADMIN_ID)

def check_admin_get():
    return request.args.get("admin_id") == str(ADMIN_ID)

@app.route("/api/admin/stats")
def admin_stats():
    if not db or not check_admin_get(): return jsonify({"error": "Unauthorized"}), 403
    return jsonify(db.get_stats())

@app.route("/api/admin/users")
def admin_users():
    if not db or not check_admin_get(): return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"users": db.get_all_users()})

@app.route("/api/admin/parcels")
def admin_parcels():
    if not db or not check_admin_get(): return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"parcels": db.get_all_parcels()})

@app.route("/api/admin/add-parcel", methods=["POST"])
def admin_add_parcel():
    if not db:
        return jsonify({"success": False, "error": "Database недоступна"})
    data = request.get_json() or {}
    if not check_admin(data): return jsonify({"error": "Unauthorized"}), 403
    if not db.get_user_by_code(data.get("client_code")):
        return jsonify({"success": False, "error": "Клиент не найден"})
    db.add_parcel(data["client_code"], data["track_number"], data.get("description"), data.get("weight"), data.get("status", "В обработке"))
    return jsonify({"success": True})

@app.route("/api/admin/update-status", methods=["POST"])
def admin_update_status():
    if not db:
        return jsonify({"success": False})
    data = request.get_json() or {}
    if not check_admin(data): return jsonify({"error": "Unauthorized"}), 403
    db.update_parcel_status(data["id"], data["status"])
    return jsonify({"success": True})

@app.route("/api/admin/delete-parcel", methods=["POST"])
def admin_delete_parcel():
    if not db:
        return jsonify({"success": False})
    data = request.get_json() or {}
    if not check_admin(data): return jsonify({"error": "Unauthorized"}), 403
    db.delete_parcel(data["id"])
    return jsonify({"success": True})

# ====================== RUN BOT ======================
def run_bot():
    try:
        from bot import main
        main()
    except Exception as e:
        print("Ошибка запуска бота:", e)

t = threading.Thread(target=run_bot, daemon=True)
t.start()

# ====================== RUN FLASK ======================
if __name__ == "__main__":
    print(f"Запуск сервера на {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=True)
