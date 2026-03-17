from flask import Flask, request, jsonify, render_template_string
import os
import sys
import threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import Database

app = Flask(__name__)
db = Database()
ADMIN_ID = int(os.getenv("ADMIN_ID", "1053328646"))

REGISTER_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZERO CARGO – Регистрация</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; min-height: 100vh; }
  .header { background: linear-gradient(135deg, #000 0%, #1a1a1a 100%); color: white; padding: 24px 20px; text-align: center; }
  .logo { font-size: 28px; font-weight: 900; letter-spacing: 2px; }
  .logo span { color: #00d4ff; }
  .subtitle { font-size: 13px; opacity: 0.7; margin-top: 4px; }
  .card { background: white; margin: 20px; border-radius: 16px; padding: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
  .section-title { font-size: 20px; font-weight: 700; margin-bottom: 20px; }
  label { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 6px; display: block; }
  input { width: 100%; padding: 14px 16px; border: 2px solid #e0e0e0; border-radius: 12px; font-size: 16px; outline: none; transition: border 0.2s; }
  input:focus { border-color: #000; }
  .btn { width: 100%; padding: 16px; background: linear-gradient(135deg, #000, #333); color: white; border: none; border-radius: 12px; font-size: 17px; font-weight: 700; cursor: pointer; margin-top: 8px; transition: transform 0.1s; }
  .btn:active { transform: scale(0.98); }
  .field { margin-bottom: 16px; }
  .features { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
  .feature { background: #f8f8f8; border-radius: 12px; padding: 14px; text-align: center; }
  .feature-icon { font-size: 24px; margin-bottom: 6px; }
  .feature-text { font-size: 12px; font-weight: 600; color: #333; }
  .feature-sub { font-size: 11px; color: #888; }
  .error { color: #e53935; font-size: 13px; margin-top: 6px; display: none; }
  .success { text-align: center; padding: 20px; }
  .success-icon { font-size: 60px; margin-bottom: 16px; }
  .code-box { background: linear-gradient(135deg, #000, #222); color: white; border-radius: 16px; padding: 20px; margin: 20px 0; text-align: center; }
  .code-label { font-size: 13px; opacity: 0.7; margin-bottom: 8px; }
  .code-value { font-size: 32px; font-weight: 900; letter-spacing: 4px; color: #00d4ff; }
  .info-row { display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #f0f0f0; font-size: 14px; }
  .info-row:last-child { border-bottom: none; }
  .info-label { color: #888; }
  .info-value { font-weight: 600; }
  #loading { display: none; text-align: center; padding: 20px; color: #888; }
</style>
</head>
<body>
<div class="header">
  <div class="logo">ZERO <span>CARGO</span></div>
  <div class="subtitle">🚛 Карго Китай → Кыргызстан</div>
</div>
<div id="form-section">
  <div class="card">
    <div class="features">
      <div class="feature"><div class="feature-icon">💰</div><div class="feature-text">2.8$ / кг</div><div class="feature-sub">Из Китая</div></div>
      <div class="feature"><div class="feature-icon">⚡</div><div class="feature-text">7–14 дней</div><div class="feature-sub">Доставка</div></div>
      <div class="feature"><div class="feature-icon">✅</div><div class="feature-text">Надёжно</div><div class="feature-sub">Гарантия</div></div>
      <div class="feature"><div class="feature-icon">📍</div><div class="feature-text">Рухий Мурас</div><div class="feature-sub">Самовывоз</div></div>
    </div>
    <div class="section-title">📝 Регистрация</div>
    <div class="field">
      <label>ФИО</label>
      <input type="text" id="fullname" placeholder="Иванов Иван Иванович" />
      <div class="error" id="err-name">Введите ФИО</div>
    </div>
    <div class="field">
      <label>Номер телефона</label>
      <input type="tel" id="phone" placeholder="+996 500 000 000" />
      <div class="error" id="err-phone">Введите номер телефона</div>
    </div>
    <button class="btn" onclick="register()">🚀 Зарегистрироваться</button>
    <div id="loading">⏳ Регистрация...</div>
  </div>
</div>
<div id="success-section" style="display:none">
  <div class="card success">
    <div class="success-icon">🎉</div>
    <h2 style="font-size:22px;margin-bottom:8px">Регистрация завершена!</h2>
    <p style="color:#888;font-size:14px;margin-bottom:16px">Добро пожаловать в ZERO CARGO</p>
    <div class="code-box">
      <div class="code-label">Ваш персональный код</div>
      <div class="code-value" id="show-code">ZC-0000</div>
    </div>
    <div id="show-details"></div>
    <p style="font-size:13px;color:#888;margin-top:16px">⚠️ Сохраните ваш код! Указывайте его при заказе товаров в Китае.</p>
  </div>
</div>
<script>
const tg = window.Telegram.WebApp;
tg.expand();
tg.setHeaderColor('#000000');
const userId = new URLSearchParams(window.location.search).get('user_id') || tg.initDataUnsafe?.user?.id;
async function register() {
  const name = document.getElementById('fullname').value.trim();
  const phone = document.getElementById('phone').value.trim();
  let valid = true;
  if (!name) { document.getElementById('err-name').style.display='block'; valid=false; } else document.getElementById('err-name').style.display='none';
  if (!phone) { document.getElementById('err-phone').style.display='block'; valid=false; } else document.getElementById('err-phone').style.display='none';
  if (!valid) return;
  document.getElementById('loading').style.display='block';
  document.querySelector('.btn').disabled = true;
  try {
    const res = await fetch('/api/register', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ telegram_id: userId, full_name: name, phone: phone }) });
    const data = await res.json();
    if (data.success) {
      document.getElementById('show-code').textContent = data.code;
      document.getElementById('show-details').innerHTML = `
        <div class="info-row"><span class="info-label">👤 ФИО</span><span class="info-value">${name}</span></div>
        <div class="info-row"><span class="info-label">📱 Телефон</span><span class="info-value">${phone}</span></div>
        <div class="info-row"><span class="info-label">📍 ПВЗ</span><span class="info-value">Рухий Мурас</span></div>`;
      document.getElementById('form-section').style.display='none';
      document.getElementById('success-section').style.display='block';
      tg.sendData(JSON.stringify({action:'registered', code: data.code}));
    } else { alert(data.error || 'Ошибка регистрации'); }
  } catch(e) { alert('Ошибка соединения'); }
  document.getElementById('loading').style.display='none';
}
</script>
</body>
</html>"""

PARCELS_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZERO CARGO – Мои посылки</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; min-height: 100vh; }
  .header { background: linear-gradient(135deg, #000 0%, #1a1a1a 100%); color: white; padding: 20px; }
  .header h1 { font-size: 22px; font-weight: 800; }
  .header p { font-size: 13px; opacity: 0.6; margin-top: 2px; }
  .tabs { display: flex; background: white; border-bottom: 1px solid #eee; }
  .tab { flex: 1; padding: 14px; text-align: center; font-size: 14px; font-weight: 600; cursor: pointer; border-bottom: 3px solid transparent; color: #888; transition: all 0.2s; }
  .tab.active { color: #000; border-bottom-color: #000; }
  .search-box { padding: 16px; background: white; border-bottom: 1px solid #eee; }
  .search-input { width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 12px; font-size: 15px; outline: none; }
  .search-input:focus { border-color: #000; }
  .search-btn { width: 100%; margin-top: 8px; padding: 12px; background: #000; color: white; border: none; border-radius: 12px; font-size: 15px; font-weight: 700; cursor: pointer; }
  .parcels-list { padding: 16px; }
  .parcel-card { background: white; border-radius: 16px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); }
  .parcel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
  .track { font-weight: 700; font-size: 15px; }
  .status { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
  .s1 { background:#fff3e0; color:#e65100; }
  .s2 { background:#e3f2fd; color:#1565c0; }
  .s3 { background:#f3e5f5; color:#6a1b9a; }
  .s4 { background:#e8f5e9; color:#2e7d32; }
  .s5 { background:#e0f7fa; color:#00695c; }
  .s6 { background:#eeeeee; color:#424242; }
  .parcel-info { font-size: 13px; color: #666; }
  .parcel-row { display: flex; justify-content: space-between; margin-top: 6px; }
  .empty { text-align: center; padding: 60px 20px; color: #aaa; }
  .empty-icon { font-size: 60px; margin-bottom: 16px; }
</style>
</head>
<body>
<div class="header">
  <h1>📦 Мои посылки</h1>
  <p id="user-code-display">Загрузка...</p>
</div>
<div class="tabs">
  <div class="tab active" onclick="showTab('all')">Все посылки</div>
  <div class="tab" onclick="showTab('search')">Поиск</div>
</div>
<div id="all-section">
  <div class="parcels-list" id="parcels-container">
    <div class="empty"><div class="empty-icon">📦</div><p>У вас пока нет посылок</p></div>
  </div>
</div>
<div id="search-section" style="display:none">
  <div class="search-box">
    <input type="text" class="search-input" id="track-input" placeholder="Введите трек-номер" />
    <button class="search-btn" onclick="searchParcel()">🔍 Найти</button>
  </div>
  <div class="parcels-list" id="search-results"></div>
</div>
<script>
const tg = window.Telegram.WebApp;
tg.expand();
tg.setHeaderColor('#000000');
const params = new URLSearchParams(window.location.search);
const clientCode = params.get('code') || '';
document.getElementById('user-code-display').textContent = 'Код: ' + clientCode;
const statusClass = {'В обработке':'s1','На складе в Китае':'s2','В пути':'s3','В Бишкеке':'s4','Готово к выдаче':'s5','Выдано':'s6'};
const statusIcon = {'В обработке':'⏳','На складе в Китае':'🇨🇳','В пути':'✈️','В Бишкеке':'🏙','Готово к выдаче':'✅','Выдано':'📬'};
function renderParcel(p) {
  const cls = statusClass[p.status] || 's1';
  const icon = statusIcon[p.status] || '📦';
  return `<div class="parcel-card"><div class="parcel-header"><span class="track">🏷 ${p.track_number}</span><span class="status ${cls}">${icon} ${p.status}</span></div><div class="parcel-info">${p.description ? `<div>📝 ${p.description}</div>` : ''}<div class="parcel-row">${p.weight ? `<span>⚖️ ${p.weight} кг</span>` : '<span></span>'}<span>📅 ${(p.created_at||'').substring(0,10)}</span></div></div></div>`;
}
async function loadParcels() {
  if (!clientCode) return;
  const res = await fetch('/api/parcels?code=' + clientCode);
  const data = await res.json();
  const container = document.getElementById('parcels-container');
  container.innerHTML = data.parcels && data.parcels.length > 0 ? data.parcels.map(renderParcel).join('') : '<div class="empty"><div class="empty-icon">📦</div><p>У вас пока нет посылок</p></div>';
}
async function searchParcel() {
  const track = document.getElementById('track-input').value.trim();
  if (!track) return;
  const res = await fetch('/api/search-parcel?track=' + track + '&code=' + clientCode);
  const data = await res.json();
  const container = document.getElementById('search-results');
  container.innerHTML = data.parcels && data.parcels.length > 0 ? data.parcels.map(renderParcel).join('') : '<div class="empty"><div class="empty-icon">🔍</div><p>Посылка не найдена</p></div>';
}
function showTab(tab) {
  document.querySelectorAll('.tab').forEach((t,i) => t.classList.toggle('active', (tab==='all'&&i===0)||(tab==='search'&&i===1)));
  document.getElementById('all-section').style.display = tab==='all' ? 'block' : 'none';
  document.getElementById('search-section').style.display = tab==='search' ? 'block' : 'none';
}
loadParcels();
</script>
</body>
</html>"""

ADMIN_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZERO CARGO – Admin</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0a0a0a; color: white; }
  .topbar { background: linear-gradient(135deg, #000, #1a1a1a); padding: 20px 24px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #333; }
  .logo { font-size: 22px; font-weight: 900; }
  .logo span { color: #00d4ff; }
  .badge { background: #00d4ff; color: #000; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; }
  .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 20px; }
  .stat-card { background: #111; border-radius: 16px; padding: 20px; border: 1px solid #333; }
  .stat-num { font-size: 36px; font-weight: 900; color: #00d4ff; }
  .stat-label { font-size: 13px; color: #888; margin-top: 4px; }
  .tabs { display: flex; background: #111; border-bottom: 1px solid #333; }
  .tab { flex: 1; padding: 14px; text-align: center; font-size: 13px; font-weight: 600; cursor: pointer; color: #888; border-bottom: 3px solid transparent; transition: all 0.2s; }
  .tab.active { color: #00d4ff; border-bottom-color: #00d4ff; }
  .section { padding: 16px; display: none; }
  .section.active { display: block; }
  .card { background: #111; border-radius: 12px; padding: 16px; margin-bottom: 12px; border: 1px solid #222; }
  .user-name { font-size: 16px; font-weight: 700; margin-bottom: 6px; }
  .user-meta { font-size: 13px; color: #888; line-height: 1.8; }
  .code { color: #00d4ff; font-weight: 700; }
  .btn { padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer; font-size: 13px; font-weight: 600; }
  .btn-primary { background: #00d4ff; color: #000; }
  .btn-danger { background: #e53935; color: white; }
  input, select { background: #1a1a1a; border: 1px solid #333; color: white; padding: 10px 14px; border-radius: 10px; font-size: 14px; width: 100%; outline: none; margin-bottom: 10px; }
  input:focus, select:focus { border-color: #00d4ff; }
  label { font-size: 13px; color: #888; margin-bottom: 4px; display: block; }
  .status-badge { padding: 3px 8px; border-radius: 20px; font-size: 11px; font-weight: 600; }
  .msg { padding: 12px; border-radius: 10px; margin-bottom: 12px; font-size: 14px; display: none; }
  .msg-ok { background: #1b5e20; color: #a5d6a7; }
  .msg-err { background: #b71c1c; color: #ef9a9a; }
  .parcel-row { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; flex-wrap: wrap; }
  .search-bar { margin-bottom: 16px; }
</style>
</head>
<body>
<div class="topbar">
  <div class="logo">ZERO <span>CARGO</span></div>
  <div class="badge">ADMIN</div>
</div>
<div class="stats">
  <div class="stat-card"><div class="stat-num" id="s-users">–</div><div class="stat-label">👥 Клиентов</div></div>
  <div class="stat-card"><div class="stat-num" id="s-parcels">–</div><div class="stat-label">📦 Посылок</div></div>
</div>
<div class="tabs">
  <div class="tab active" onclick="switchTab('users')">👥 Клиенты</div>
  <div class="tab" onclick="switchTab('parcels')">📦 Посылки</div>
  <div class="tab" onclick="switchTab('add')">➕ Добавить</div>
</div>
<div id="tab-users" class="section active">
  <div class="search-bar"><input type="text" id="search-user" placeholder="Поиск по имени или коду..." oninput="filterUsers()" /></div>
  <div id="users-list">Загрузка...</div>
</div>
<div id="tab-parcels" class="section">
  <div class="search-bar"><input type="text" id="search-parcel" placeholder="Поиск по трек-номеру..." oninput="filterParcels()" /></div>
  <div id="parcels-list">Загрузка...</div>
</div>
<div id="tab-add" class="section">
  <div class="card">
    <h3 style="margin-bottom:16px">➕ Добавить посылку</h3>
    <div id="msg-add" class="msg"></div>
    <label>Код клиента</label><input id="a-code" placeholder="ZC-1001" />
    <label>Трек-номер</label><input id="a-track" placeholder="CN123456789" />
    <label>Описание</label><input id="a-desc" placeholder="Одежда, электроника..." />
    <label>Вес (кг)</label><input id="a-weight" type="number" step="0.1" placeholder="1.5" />
    <label>Статус</label>
    <select id="a-status">
      <option>В обработке</option>
      <option>На складе в Китае</option>
      <option>В пути</option>
      <option>В Бишкеке</option>
      <option>Готово к выдаче</option>
      <option>Выдано</option>
    </select>
    <button class="btn btn-primary" style="width:100%;padding:14px;margin-top:4px" onclick="addParcel()">Добавить посылку</button>
  </div>
</div>
<script>
const ADMIN_ID = {{ admin_id }};
let allUsers = [], allParcels = [];
async function loadStats() {
  const r = await fetch('/api/admin/stats?admin_id=' + ADMIN_ID);
  const d = await r.json();
  document.getElementById('s-users').textContent = d.users || 0;
  document.getElementById('s-parcels').textContent = d.parcels || 0;
}
async function loadUsers() {
  const r = await fetch('/api/admin/users?admin_id=' + ADMIN_ID);
  const d = await r.json();
  allUsers = d.users || [];
  renderUsers(allUsers);
}
function renderUsers(users) {
  const el = document.getElementById('users-list');
  if (!users.length) { el.innerHTML = '<div style="color:#888;text-align:center;padding:40px">Нет клиентов</div>'; return; }
  el.innerHTML = users.map(u => `<div class="card"><div class="user-name">${u.full_name}</div><div class="user-meta"><div>🔑 Код: <span class="code">${u.client_code}</span></div><div>📱 ${u.phone}</div><div>📅 ${(u.created_at||'').substring(0,10)}</div><div>🌐 ${u.language==='kg'?'Кыргызча':'Русский'}</div></div></div>`).join('');
}
function filterUsers() {
  const q = document.getElementById('search-user').value.toLowerCase();
  renderUsers(allUsers.filter(u => u.full_name.toLowerCase().includes(q) || u.client_code.toLowerCase().includes(q) || u.phone.includes(q)));
}
async function loadParcels() {
  const r = await fetch('/api/admin/parcels?admin_id=' + ADMIN_ID);
  const d = await r.json();
  allParcels = d.parcels || [];
  renderParcels(allParcels);
}
const sColors = {'В обработке':'#ff9800','На складе в Китае':'#2196f3','В пути':'#9c27b0','В Бишкеке':'#4caf50','Готово к выдаче':'#00bcd4','Выдано':'#9e9e9e'};
function renderParcels(parcels) {
  const el = document.getElementById('parcels-list');
  if (!parcels.length) { el.innerHTML = '<div style="color:#888;text-align:center;padding:40px">Нет посылок</div>'; return; }
  el.innerHTML = parcels.map(p => `<div class="card"><div class="parcel-row"><div><div style="font-weight:700;margin-bottom:4px">🏷 ${p.track_number}</div><div style="font-size:13px;color:#888">📦 ${p.client_code} | ${p.description||'—'} | ${p.weight||'—'} кг</div><div style="font-size:12px;color:#666;margin-top:4px">📅 ${(p.created_at||'').substring(0,10)}</div></div><div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end"><span class="status-badge" style="background:${sColors[p.status]||'#555'}22;color:${sColors[p.status]||'#aaa'}">${p.status}</span><select onchange="updateStatus(${p.id},this.value)" style="font-size:12px;padding:4px 8px;width:auto;margin:0"><option value="">Изменить</option><option>В обработке</option><option>На складе в Китае</option><option>В пути</option><option>В Бишкеке</option><option>Готово к выдаче</option><option>Выдано</option></select><button class="btn btn-danger" style="padding:4px 10px;font-size:12px" onclick="deleteParcel(${p.id})">🗑</button></div></div></div>`).join('');
}
function filterParcels() {
  const q = document.getElementById('search-parcel').value.toLowerCase();
  renderParcels(allParcels.filter(p => p.track_number.toLowerCase().includes(q) || p.client_code.toLowerCase().includes(q)));
}
async function updateStatus(id, status) {
  if (!status) return;
  await fetch('/api/admin/update-status', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,status,admin_id:ADMIN_ID})});
  loadParcels(); loadStats();
}
async function deleteParcel(id) {
  if (!confirm('Удалить посылку?')) return;
  await fetch('/api/admin/delete-parcel', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,admin_id:ADMIN_ID})});
  loadParcels(); loadStats();
}
async function addParcel() {
  const msg = document.getElementById('msg-add');
  const data = { client_code: document.getElementById('a-code').value.trim(), track_number: document.getElementById('a-track').value.trim(), description: document.getElementById('a-desc').value.trim(), weight: parseFloat(document.getElementById('a-weight').value)||null, status: document.getElementById('a-status').value, admin_id: ADMIN_ID };
  if (!data.client_code || !data.track_number) { msg.textContent='Заполните код клиента и трек-номер'; msg.className='msg msg-err'; msg.style.display='block'; return; }
  const r = await fetch('/api/admin/add-parcel',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const d = await r.json();
  msg.textContent = d.success ? '✅ Посылка добавлена!' : (d.error||'Ошибка');
  msg.className = d.success ? 'msg msg-ok' : 'msg msg-err';
  msg.style.display='block';
  if (d.success) { ['a-code','a-track','a-desc','a-weight'].forEach(id=>document.getElementById(id).value=''); loadParcels(); loadStats(); }
}
function switchTab(name) {
  document.querySelectorAll('.tab').forEach((t,i)=>{ const tabs=['users','parcels','add']; t.classList.toggle('active',tabs[i]===name); });
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
}
loadStats(); loadUsers(); loadParcels();
setInterval(()=>{ loadStats(); loadUsers(); loadParcels(); }, 30000);
</script>
</body>
</html>"""

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
        return jsonify({"success": True, "code": existing["client_code"], "already": True})
    code = db.register_user(int(tid), name, phone)
    if code:
        return jsonify({"success": True, "code": code})
    return jsonify({"success": False, "error": "Ошибка регистрации"})

@app.route("/api/user")
def api_get_user():
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
    data = request.get_json()
    db.update_language(int(data["telegram_id"]), data["language"])
    return jsonify({"success": True})

@app.route("/api/parcels")
def api_parcels():
    code = request.args.get("code", "")
    return jsonify({"parcels": db.get_parcels_by_code(code)})

@app.route("/api/search-parcel")
def api_search_parcel():
    track = request.args.get("track", "")
    code = request.args.get("code", "")
    results = [p for p in db.search_parcel_by_track(track) if p["client_code"] == code]
    return jsonify({"parcels": results})

def check_admin(data):
    return str(data.get("admin_id")) == str(ADMIN_ID)

def check_admin_get():
    return request.args.get("admin_id") == str(ADMIN_ID)

@app.route("/api/admin/stats")
def admin_stats():
    if not check_admin_get(): return jsonify({"error": "Unauthorized"}), 403
    return jsonify(db.get_stats())

@app.route("/api/admin/users")
def admin_users():
    if not check_admin_get(): return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"users": db.get_all_users()})

@app.route("/api/admin/parcels")
def admin_parcels():
    if not check_admin_get(): return jsonify({"error": "Unauthorized"}), 403
    return jsonify({"parcels": db.get_all_parcels()})

@app.route("/api/admin/add-parcel", methods=["POST"])
def admin_add_parcel():
    data = request.get_json()
    if not check_admin(data): return jsonify({"error": "Unauthorized"}), 403
    if not db.get_user_by_code(data["client_code"]):
        return jsonify({"success": False, "error": "Клиент не найден"})
    db.add_parcel(data["client_code"], data["track_number"], data.get("description"), data.get("weight"), data.get("status", "В обработке"))
    return jsonify({"success": True})

@app.route("/api/admin/update-status", methods=["POST"])
def admin_update_status():
    data = request.get_json()
    if not check_admin(data): return jsonify({"error": "Unauthorized"}), 403
    db.update_parcel_status(data["id"], data["status"])
    return jsonify({"success": True})

@app.route("/api/admin/delete-parcel", methods=["POST"])
def admin_delete_parcel():
    data = request.get_json()
    if not check_admin(data): return jsonify({"error": "Unauthorized"}), 403
    db.delete_parcel(data["id"])
    return jsonify({"success": True})

def run_bot():
    from bot import main
    main()

if __name__ == "__main__":
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
