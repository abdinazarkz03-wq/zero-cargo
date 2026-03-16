import asyncpg
from config import DATABASE_URL

db_pool = None

async def connect():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)

async def get_user(user_id):
    async with db_pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)

async def register_user(user_id, full_name, phone, address):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (user_id, full_name, phone, address, personal_code, china_code) "
            "VALUES ($1,$2,$3,$4,$5,$6)",
            user_id, full_name, phone, address, f"CODE{user_id}", "VXMMM"
        )
        return await get_user(user_id)

async def get_user_with_parcels(user_id):
    async with db_pool.acquire() as conn:
        user = await get_user(user_id)
        if not user:
            return None
        parcels = await conn.fetch("SELECT * FROM parcels WHERE user_id=$1 ORDER BY created_at DESC", user_id)
        return {
            "user": dict(user),
            "parcels": [dict(p) for p in parcels]
        }

async def add_parcel(user_id, track_code):
    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO parcels (user_id, track_code, status, created_at) VALUES ($1,$2,$3,NOW())",
            user_id, track_code, "В ожидании"
        )
        return True

async def get_user_parcels(user_id):
    async with db_pool.acquire() as conn:
        parcels = await conn.fetch("SELECT * FROM parcels WHERE user_id=$1 ORDER BY created_at DESC", user_id)
        return [dict(p) for p in parcels]

async def get_all_users():
    async with db_pool.acquire() as conn:
        users = await conn.fetch("SELECT *, (SELECT COUNT(*) FROM parcels p WHERE p.user_id=u.user_id) as parcels_count FROM users u ORDER BY full_name")
        return [dict(u) for u in users]

async def set_language(user_id, lang):
    async with db_pool.acquire() as conn:
        await conn.execute("UPDATE users SET language=$1 WHERE user_id=$2", lang, user_id)

async def get_stats():
    async with db_pool.acquire() as conn:
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users")
        total_parcels = await conn.fetchval("SELECT COUNT(*) FROM parcels")
        today_users = await conn.fetchval("SELECT COUNT(*) FROM users WHERE created_at::date = CURRENT_DATE")
        status_stats_raw = await conn.fetch("SELECT status, COUNT(*) as count FROM parcels GROUP BY status")
        status_stats = {r['status']: r['count'] for r in status_stats_raw}
        return {
            "total_users": total_users,
            "total_parcels": total_parcels,
            "today_users": today_users,
            "status_stats": status_stats
        }
