from flask import Flask, request, jsonify, render_template_string
from database import Database
import os

app = Flask(__name__)
db = Database()

# --- СТИЛЬНЫЙ ДИЗАЙН (HTML) ---

REGISTER_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zero Cargo - Регистрация</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, sans-serif; background: #000; color: #fff; }
  .header { padding: 40px 20px; text-align: center; }
  .logo { font-size: 32px; font-weight: 900; letter-spacing: 3px; }
  .logo span { color: #f3d01a; } /* Желтый акцент для стиля */
  .container { padding: 0 25px; }
  .card { background: #1a1a1a; border-radius: 20px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
  .title { font-size: 22px; font-weight: 700; margin-bottom: 20px; text-align: center; }
  label { display: block; font-size: 13px; color: #888; margin-bottom: 8px; margin-left: 5px; }
  input { width: 100%; padding: 16px; background: #262626; border: 1px solid #333; border-radius: 12px; color: #fff; font-size: 16px; margin-bottom: 20px; outline: none; }
  input:focus { border-color: #f3d01a; }
  .btn { width: 100%; padding: 18px; background: #fff; color: #000; border: none; border-radius: 12px; font-size: 17px; font-weight: 800; cursor: pointer; }
  .success { display: none; text-align: center; }
  .code-box { background: #f3d01a; color: #000; padding: 20px; border-radius: 15px; font-size: 28px; font-weight: 900; margin: 20px 0; }
</style>
</head>
<body>
  <div class="header">
    <div class="logo">ZERO<span>CARGO</span></div>
  </div>
  <div class="container">
    <div class="card" id="form-section">
      <div class="title">Регистрация клиента</div>
      <label>ВАШЕ ФИО</label>
      <input type="text" id="fullname" placeholder="Иван Иванов">
      <label>НОМЕР ТЕЛЕФОНА</label>
      <input type="tel" id="phone" placeholder="+996 --- -- -- --">
      <button class="btn" onclick="register()">ПОЛУЧИТЬ КОД</button>
    </div>
    
    <div class="card success" id="success-section">
      <div style="font-size: 50px;">✅</div>
      <div class="title">Вы успешно зарегистрированы!</div>
      <p style="color: #888;">Ваш личный код для заказов:</p>
      <div class="code-box" id="show-code">ZC-1001</div>
      <p style="font-size: 14px; color: #f3d01a;">Сохраните его и указывайте в адресе!</p>
    </div>
  </div>

<script>
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();
tg.MainButton.hide();

async function register() {
  const name = document.getElementById('fullname').value;
  const phone = document.getElementById('phone').value;
  if(!name || !phone) { alert('Заполните все поля!'); return; }

  const telegram_id = tg.initDataUnsafe?.user?.id || 0;
  
  try {
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({telegram_id, full_name: name, phone})
    });
    const data = await res.json();
    if(data.success) {
      document.getElementById('form-section').style.display = 'none';
      document.getElementById('success-section').style.display = 'block';
      document.getElementById('show-code').textContent = data.client_code;
      // Закрываем через 5 секунд
      setTimeout(() => tg.close(), 5000);
    }
  } catch(e) { alert('Ошибка сети'); }
}
</script>
</body>
</html>
"""

# Остальные части (PARCELS_HTML и ADMIN_HTML) остаются такими же или меняются под черный стиль
# ... (код маршрутов из твоего старого webapp.py) ...

@app.route("/")
def index(): return "Zero Cargo API Running"

@app.route("/register")
def register_page(): return render_template_string(REGISTER_HTML)

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    code = db.create_user(data['telegram_id'], data['full_name'], data['phone'])
    return jsonify({"success": True, "client_code": code})

# Добавь сюда свои остальные маршруты из старого webapp.py (parcels, admin и т.д.)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
