from flask import Flask, request, jsonify, render_template_string
from database import Database
import os

app = Flask(__name__)
db = Database()
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1053328646"))

STATUSES = {
    "pending": {"ru": "⏳ Ожидается", "ky": "⏳ Күтүүдө"},
    "in_china": {"ru": "🇨🇳 На складе в Китае", "ky": "🇨🇳 Кытай кампасында"},
    "in_transit": {"ru": "✈️ В пути", "ky": "✈️ Жолдо"},
    "in_bishkek": {"ru": "🇰🇬 В Бишкеке", "ky": "🇰🇬 Бишкекте"},
    "ready": {"ru": "✅ Готово к выдаче", "ky": "✅ Берүүгө даяр"},
    "delivered": {"ru": "📦 Выдано", "ky": "📦 Берилди"},
}

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
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; min-height: 100vh; }
  .header { background: #000; color: white; padding: 20px; text-align: center; }
  .logo { font-size: 28px; font-weight: 900; letter-spacing: 2px; }
  .logo span { color: #888; }
  .subtitle { font-size: 13px; color: #aaa; margin-top: 4px; }
  .container { padding: 24px 20px; max-width: 500px; margin: 0 auto; }
  .title { font-size: 22px; font-weight: 700; text-align: center; margin-bottom: 24px; }
  .form-group { margin-bottom: 18px; }
  label { display: block; font-size: 14px; font-weight: 600; color: #333; margin-bottom: 8px; }
  input { width: 100%; padding: 14px 16px; border: 1.5px solid #ddd; border-radius: 12px; font-size: 16px; outline: none; transition: border-color 0.2s; background: white; }
  input:focus { border-color: #000; }
  .btn { width: 100%; padding: 16px; background: #000; color: white; border: none; border-radius: 14px; font-size: 17px; font-weight: 700; cursor: pointer; margin-top: 8px; letter-spacing: 0.5px; }
  .btn:active { opacity: 0.9; transform: scale(0.99); }
  .success { background: #f0fff4; border: 1.5px solid #48bb78; border-radius: 14px; padding: 20px; text-align: center; display: none; }
  .success-icon { font-size: 48px; margin-bottom: 12px; }
  .success h2 { color: #2f855a; font-size: 20px; margin-bottom: 8px; }
  .code-box { background: #000; color: white; border-radius: 12px; padding: 16px; margin: 16px 0; font-size: 24px; font-weight: 900; letter-spacing: 3px; text-align: center; }
  .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; font-size: 14px; }
  .info-row:last-child { border-bottom: none; }
  .info-label { color: #666; }
  .info-value { font-weight: 600; }
  .error { color: #e53e3e; font-size: 13px; margin-top: 6px; display: none; }
</style>
</head>
<body>
<div class="header">
  <div class="logo">ZERO <span>CARGO</span></div>
  <div class="subtitle">Карго Китай 🚛</div>
</div>
<div class="container">
  <div id="form-section">
    <div class="title">📝 Регистрация</div>
    <div class="form-group">
      <label>ФИО</label>
      <input type="text" id="fullname" placeholder="Введите ваше ФИО" autocomplete="name">
      <div class="error" id="name-error">Введите ФИО</div>
    </div>
    <div class="form-group">
      <label>Номер телефона</label>
      <input type="tel" id="phone" placeholder="+996 XXX XX XX XX">
      <div class="error" id="phone-error">Введите номер телефона</div>
    </div>
    <button class="btn" onclick="register()">Зарегистрироваться</button>
  </div>
  <div class="success" id="success-section">
    <div class="success-icon">✅</div>
    <h2>Регистрация завершена!</h2>
    <p style="color:#555;margin-bottom:12px;">Ваши данные:</p>
    <div class="code-box" id="show-code">ZC-0000</div>
    <div id="user-info"></div>
    <p style="margin-top:12px;color:#666;font-size:13px;">📞 Менеджер: +996505600542</p>
  </div>
</div>
<script>
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

async function register() {
  const name = document.getElementById('fullname').value.trim();
  const phone = document.getElementById('phone').value.trim();
  let valid = true;
  document.getElementById('name-error').style.display = 'none';
  document.getElementById('phone-error').style.display = 'none';
  if (!name || name.length < 2) { document.getElementById('name-error').style.display = 'block'; valid = false; }
  if (!phone || phone.length < 7) { document.getElementById('phone-error').style.display = 'block'; valid = false; }
  if (!valid) return;
  const user = tg.initDataUnsafe?.user;
  const telegram_id = user?.id || 0;
  const lang = user?.language_code === 'ky' ? 'ky' : 'ru';
  try {
    const resp = await fetch('/api/register', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({telegram_id, full_name: name, phone, language: lang})
    });
    const data = await resp.json();
    if (data.success) {
      document.getElementById('form-section').style.display = 'none';
      document.getElementById('success-section').style.display = 'block';
      document.getElementById('show-code').textContent = data.client_code;
      document.getElementById('user-info').innerHTML = `
        <div class="info-row"><span class="info-label">👤 ФИО</span><span class="info-value">${name}</span></div>
        <div class="info-row"><span class="info-label">📱 Телефон</span><span class="info-value">${phone}</span></div>
        <div class="info-row"><span class="info-label">📍 ПВЗ</span><span class="info-value">ж/м Рухий Мурас</span></div>
      `;
      tg.sendData(JSON.stringify({action: 'registered', code: data.client_code}));
      setTimeout(() => tg.close(), 3000);
    } else {
      alert(data.error || 'Ошибка регистрации');
    }
  } catch(e) { alert('Ошибка соединения'); }
}
</script>
</body>
</html>
"""

PARCELS_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zero Cargo - Мои посылки</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; min-height: 100vh; }
  .header { background: #000; color: white; padding: 20px; text-align: center; }
  .logo { font-size: 22px; font-weight: 900; letter-spacing: 2px; }
  .container { padding: 16px; max-width: 500px; margin: 0 auto; }
  .title { font-size: 22px; font-weight: 700; text-align: center; margin: 16px 0; }
  .tabs { display: flex; background: #eee; border-radius: 12px; padding: 4px; margin-bottom: 16px; }
  .tab { flex: 1; padding: 10px; text-align: center; border-radius: 10px; cursor: pointer; font-weight: 600; font-size: 14px; transition: all 0.2s; }
  .tab.active { background: white; box-shadow: 0 1px 4px rgba(0,0,0,0.15); color: #000; }
  .search-box { display: flex; gap: 8px; margin-bottom: 16px; }
  .search-box input { flex: 1; padding: 12px 16px; border: 1.5px solid #ddd; border-radius: 12px; font-size: 15px; outline: none; }
  .search-box input:focus { border-color: #000; }
  .btn-search { padding: 12px 20px; background: #000; color: white; border: none; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; }
  .empty { text-align: center; padding: 60px 20px; color: #888; }
  .empty-icon { font-size: 64px; margin-bottom: 12px; }
  .parcel-card { background: white; border-radius: 14px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 6px rgba(0,0,0,0.08); }
  .parcel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
  .track { font-weight: 700; font-size: 15px; }
  .status-badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
  .status-pending { background: #fff3cd; color: #856404; }
  .status-in_china { background: #cfe2ff; color: #084298; }
  .status-in_transit { background: #d1ecf1; color: #0c5460; }
  .status-in_bishkek { background: #d4edda; color: #155724; }
  .status-ready { background: #d4edda; color: #155724; }
  .status-delivered { background: #e2e3e5; color: #383d41; }
  .parcel-info { font-size: 13px; color: #555; }
  .parcel-row { display: flex; justify-content: space-between; padding: 3px 0; }
</style>
</head>
<body>
<div class="header">
  <div class="logo">ZERO CARGO</div>
</div>
<div class="container">
  <div class="title">📦 Мои посылки</div>
  <div class="tabs">
    <div class="tab active" onclick="showTab('all')">Все посылки</div>
    <div class="tab" onclick="showTab('search')">Поиск</div>
  </div>
  <div id="search-section" style="display:none">
    <div class="search-box">
      <input type="text" id="track-input" placeholder="Введите трек-номер">
      <button class="btn-search" onclick="searchParcel()">Найти</button>
    </div>
  </div>
  <div id="parcels-list"></div>
</div>
<script>
const tg = window.Telegram.WebApp;
tg.ready(); tg.expand();
const params = new URLSearchParams(window.location.search);
const userId = params.get('user_id') || tg.initDataUnsafe?.user?.id || 0;
const statusLabels = {
  pending: '⏳ Ожидается', in_china: '🇨🇳 На складе в Китае',
  in_transit: '✈️ В пути', in_bishkek: '🇰🇬 В Бишкеке',
  ready: '✅ Готово к выдаче', delivered: '📦 Выдано'
};
function showTab(tab) {
  document.querySelectorAll('.tab').forEach((t,i) => t.classList.toggle('active', (tab==='all'&&i===0)||(tab==='search'&&i===1)));
  document.getElementById('search-section').style.display = tab==='search'?'block':'none';
  if(tab==='all') loadParcels();
  else document.getElementById('parcels-list').innerHTML='';
}
function renderParcels(parcels) {
  const list = document.getElementById('parcels-list');
  if(!parcels.length) {
    list.innerHTML = '<div class="empty"><div class="empty-icon">📦</div><p>У вас пока нет посылок</p></div>';
    return;
  }
  list.innerHTML = parcels.map(p => `
    <div class="parcel-card">
      <div class="parcel-header">
        <span class="track">📦 ${p.track_number || 'Без трека'}</span>
        <span class="status-badge status-${p.status}">${statusLabels[p.status]||p.status}</span>
      </div>
      <div class="parcel-info">
        ${p.description ? `<div class="parcel-row"><span>📋 Описание:</span><span>${p.description}</span></div>` : ''}
        ${p.weight ? `<div class="parcel-row"><span>⚖️ Вес:</span><span>${p.weight} кг</span></div>` : ''}
        <div class="parcel-row"><span>📅 Дата:</span><span>${p.created_at?.slice(0,10)}</span></div>
      </div>
    </div>
  `).join('');
}
async function loadParcels() {
  try {
    const r = await fetch('/api/parcels?user_id='+userId);
    const data = await r.json();
    renderParcels(data.parcels || []);
  } catch(e) { document.getElementById('parcels-list').innerHTML='<div class="empty"><p>Ошибка загрузки</p></div>'; }
}
async function searchParcel() {
  const track = document.getElementById('track-input').value.trim();
  if(!track) return;
  try {
    const r = await fetch('/api/parcels/search?track='+encodeURIComponent(track)+'&user_id='+userId);
    const data = await r.json();
    renderParcels(data.parcels || []);
  } catch(e) {}
}
loadParcels();
</script>
</body>
</html>
"""

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Zero Cargo - Админ</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f0f0; min-height: 100vh; }
  .header { background: #000; color: white; padding: 16px 20px; }
  .header h1 { font-size: 18px; font-weight: 800; letter-spacing: 1px; }
  .tabs { display: flex; background: #eee; border-bottom: 1px solid #ddd; }
  .tab { flex: 1; padding: 14px; text-align: center; cursor: pointer; font-weight: 600; font-size: 13px; border-bottom: 3px solid transparent; }
  .tab.active { border-bottom-color: #000; color: #000; background: white; }
  .container { padding: 16px; max-width: 600px; margin: 0 auto; }
  .card { background: white; border-radius: 14px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
  .card h3 { font-size: 15px; margin-bottom: 12px; color: #333; border-bottom: 1px solid #eee; padding-bottom: 8px; }
  .form-row { display: flex; flex-direction: column; gap: 10px; }
  input, select { padding: 11px 14px; border: 1.5px solid #ddd; border-radius: 10px; font-size: 14px; outline: none; width: 100%; }
  input:focus, select:focus { border-color: #000; }
  .btn { padding: 12px 20px; background: #000; color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; width: 100%; }
  .btn-sm { padding: 6px 14px; font-size: 12px; width: auto; border-radius: 8px; }
  .btn-danger { background: #ff3b30; }
  .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
  .stat-box { background: white; border-radius: 12px; padding: 16px; text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }
  .stat-num { font-size: 28px; font-weight: 900; }
  .stat-label { font-size: 12px; color: #888; margin-top: 4px; }
  .user-row, .parcel-row { background: white; border-radius: 10px; padding: 12px; margin-bottom: 8px; font-size: 13px; }
  .row-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
  .row-code { font-weight: 700; font-size: 14px; }
  .actions { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
  .status-select { padding: 6px 10px; font-size: 12px; border-radius: 8px; border: 1px solid #ddd; }
  .search-bar { margin-bottom: 12px; }
  .tag { display: inline-block; background: #eee; border-radius: 6px; padding: 2px 8px; font-size: 11px; margin-right: 4px; }
</style>
</head>
<body>
<div class="header">
  <div style="font-size:10px;color:#888;letter-spacing:1px">ZERO CARGO</div>
  <h1>🔧 Админ-панель</h1>
</div>
<div class="tabs">
  <div class="tab active" onclick="showTab('dashboard')">📊 Главная</div>
  <div class="tab" onclick="showTab('parcels')">📦 Посылки</div>
  <div class="tab" onclick="showTab('users')">👥 Клиенты</div>
  <div class="tab" onclick="showTab('add')">➕ Добавить</div>
</div>
<div id="tab-dashboard" class="container">
  <div class="stat-grid" id="stats"></div>
  <div class="card">
    <h3>📦 Последние посылки</h3>
    <div id="recent-parcels"></div>
  </div>
</div>
<div id="tab-parcels" class="container" style="display:none">
  <div class="search-bar"><input type="text" id="parcel-search" placeholder="Поиск по трек-номеру или коду..." oninput="filterParcels()"></div>
  <div id="all-parcels"></div>
</div>
<div id="tab-users" class="container" style="display:none">
  <div class="search-bar"><input type="text" id="user-search" placeholder="Поиск по имени или коду..." oninput="filterUsers()"></div>
  <div id="all-users"></div>
</div>
<div id="tab-add" class="container" style="display:none">
  <div class="card">
    <h3>➕ Добавить посылку</h3>
    <div class="form-row">
      <input type="text" id="add-code" placeholder="Код клиента (ZC-XXXX)">
      <input type="text" id="add-track" placeholder="Трек-номер">
      <input type="text" id="add-desc" placeholder="Описание товара">
      <input type="number" id="add-weight" placeholder="Вес (кг)" step="0.1">
      <select id="add-status">
        <option value="pending">⏳ Ожидается</option>
        <option value="in_china">🇨🇳 На складе в Китае</option>
        <option value="in_transit">✈️ В пути</option>
        <option value="in_bishkek">🇰🇬 В Бишкеке</option>
        <option value="ready">✅ Готово к выдаче</option>
        <option value="delivered">📦 Выдано</option>
      </select>
      <button class="btn" onclick="addParcel()">Добавить посылку</button>
    </div>
  </div>
</div>
<script>
const tg = window.Telegram.WebApp;
tg.ready(); tg.expand();
let allParcels = [], allUsers = [];
const statusLabels = {
  pending:'⏳ Ожидается', in_china:'🇨🇳 Склад Китай',
  in_transit:'✈️ В пути', in_bishkek:'🇰🇬 Бишкек',
  ready:'✅ К выдаче', delivered:'📦 Выдано'
};
function showTab(name) {
  ['dashboard','parcels','users','add'].forEach(t => {
    document.getElementById('tab-'+t).style.display = t===name?'block':'none';
  });
  document.querySelectorAll('.tab').forEach((el,i) => {
    el.classList.toggle('active', ['dashboard','parcels','users','add'][i]===name);
  });
  if(name==='parcels') renderParcels(allParcels);
  if(name==='users') renderUsers(allUsers);
}
async function loadData() {
  const [ps, us] = await Promise.all([
    fetch('/api/admin/parcels').then(r=>r.json()),
    fetch('/api/admin/users').then(r=>r.json())
  ]);
  allParcels = ps.parcels || [];
  allUsers = us.users || [];
  const statusCount = {};
  allParcels.forEach(p => { statusCount[p.status] = (statusCount[p.status]||0)+1; });
  document.getElementById('stats').innerHTML = `
    <div class="stat-box"><div class="stat-num">${allUsers.length}</div><div class="stat-label">👥 Клиентов</div></div>
    <div class="stat-box"><div class="stat-num">${allParcels.length}</div><div class="stat-label">📦 Посылок</div></div>
    <div class="stat-box"><div class="stat-num">${statusCount['in_transit']||0}</div><div class="stat-label">✈️ В пути</div></div>
    <div class="stat-box"><div class="stat-num">${statusCount['ready']||0}</div><div class="stat-label">✅ К выдаче</div></div>
  `;
  document.getElementById('recent-parcels').innerHTML = allParcels.slice(0,5).map(p => `
    <div style="padding:8px 0;border-bottom:1px solid #eee;font-size:13px;display:flex;justify-content:space-between">
      <span><b>${p.client_code}</b> · ${p.track_number||'—'}</span>
      <span>${statusLabels[p.status]||p.status}</span>
    </div>
  `).join('') || '<p style="color:#888;text-align:center;padding:20px">Посылок нет</p>';
}
function renderParcels(list) {
  document.getElementById('all-parcels').innerHTML = list.length ? list.map(p => `
    <div class="parcel-row">
      <div class="row-header">
        <span class="row-code">📦 ${p.track_number||'Без трека'}</span>
        <span class="tag">${p.client_code}</span>
      </div>
      <div style="color:#555;font-size:12px">${p.full_name||''} · ${p.description||''} · ${p.weight?p.weight+'кг':''}</div>
      <div class="actions">
        <select class="status-select" onchange="updateStatus(${p.id}, this.value)">
          ${Object.entries(statusLabels).map(([k,v])=>`<option value="${k}" ${p.status===k?'selected':''}>${v}</option>`).join('')}
        </select>
        <button class="btn btn-sm btn-danger" onclick="deleteParcel(${p.id})">🗑</button>
      </div>
    </div>
  `).join('') : '<p style="color:#888;text-align:center;padding:20px">Посылок нет</p>';
}
function renderUsers(list) {
  document.getElementById('all-users').innerHTML = list.length ? list.map(u => `
    <div class="user-row">
      <div class="row-header">
        <span class="row-code">👤 ${u.full_name}</span>
        <span class="tag">${u.client_code}</span>
      </div>
      <div style="color:#555;font-size:12px">📱 ${u.phone} · 🗓 ${u.created_at?.slice(0,10)}</div>
    </div>
  `).join('') : '<p style="color:#888;text-align:center;padding:20px">Клиентов нет</p>';
}
function filterParcels() {
  const q = document.getElementById('parcel-search').value.toLowerCase();
  renderParcels(allParcels.filter(p =>
    (p.track_number||'').toLowerCase().includes(q) ||
    (p.client_code||'').toLowerCase().includes(q) ||
    (p.full_name||'').toLowerCase().includes(q)
  ));
}
function filterUsers() {
  const q = document.getElementById('user-search').value.toLowerCase();
  renderUsers(allUsers.filter(u =>
    (u.full_name||'').toLowerCase().includes(q) ||
    (u.client_code||'').toLowerCase().includes(q)
  ));
}
async function updateStatus(id, status) {
  await fetch('/api/admin/parcel/status', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id, status})});
  await loadData();
  renderParcels(allParcels);
}
async function deleteParcel(id) {
  if(!confirm('Удалить посылку?')) return;
  await fetch('/api/admin/parcel/delete', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({id})});
  await loadData();
  renderParcels(allParcels);
}
async function addParcel() {
  const code = document.getElementById('add-code').value.trim();
  const track = document.getElementById('add-track').value.trim();
  const desc = document.getElementById('add-desc').value.trim();
  const weight = document.getElementById('add-weight').value;
  const status = document.getElementById('add-status').value;
  if(!code) { alert('Введите код клиента'); return; }
  const r = await fetch('/api/admin/parcel/add', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({client_code:code, track_number:track, description:desc, weight:parseFloat(weight)||null, status})
  });
  const data = await r.json();
  if(data.success) {
    alert('✅ Посылка добавлена!');
    ['add-code','add-track','add-desc','add-weight'].forEach(id => document.getElementById(id).value='');
    await loadData();
  } else { alert(data.error || 'Ошибка'); }
}
loadData();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return "<h2>Zero Cargo Bot API</h2><p>Running ✅</p>"

@app.route("/register")
def register_page():
    return render_template_string(REGISTER_HTML)

@app.route("/parcels")
def parcels_page():
    return render_template_string(PARCELS_HTML)

@app.route("/admin")
def admin_page():
    return render_template_string(ADMIN_HTML)

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    telegram_id = data.get("telegram_id")
    full_name = data.get("full_name", "").strip()
    phone = data.get("phone", "").strip()
    language = data.get("language", "ru")
    if not telegram_id or not full_name or not phone:
        return jsonify({"success": False, "error": "Заполните все поля"})
    existing = db.get_user(telegram_id)
    if existing:
        return jsonify({"success": True, "client_code": existing["client_code"], "already_exists": True})
    code = db.create_user(telegram_id, full_name, phone, language)
    return jsonify({"success": True, "client_code": code})

@app.route("/api/parcels")
def api_parcels():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"parcels": []})
    parcels = db.get_user_parcels(int(user_id))
    return jsonify({"parcels": parcels})

@app.route("/api/parcels/search")
def api_search():
    track = request.args.get("track", "")
    user_id = request.args.get("user_id")
    parcels = db.search_parcel(track)
    if user_id:
        user = db.get_user(int(user_id))
        if user:
            parcels = [p for p in parcels if p["client_code"] == user["client_code"]]
    return jsonify({"parcels": parcels})

@app.route("/api/admin/parcels")
def api_admin_parcels():
    return jsonify({"parcels": db.get_all_parcels()})

@app.route("/api/admin/users")
def api_admin_users():
    return jsonify({"users": db.get_all_users()})

@app.route("/api/admin/parcel/add", methods=["POST"])
def api_add_parcel():
    data = request.json
    success = db.add_parcel(
        data["client_code"], data.get("track_number"),
        data.get("description"), data.get("weight"), data.get("status", "pending")
    )
    if success:
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Клиент с таким кодом не найден"})

@app.route("/api/admin/parcel/status", methods=["POST"])
def api_update_status():
    data = request.json
    db.update_parcel_status(data["id"], data["status"])
    return jsonify({"success": True})

@app.route("/api/admin/parcel/delete", methods=["POST"])
def api_delete_parcel():
    data = request.json
    db.delete_parcel(data["id"])
    return jsonify({"success": True})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
