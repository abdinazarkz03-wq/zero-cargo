import asyncpg

class DB:
    def __init__(self):
        self.pool = None

    async def connect(self):
        from config import DATABASE_URL
        self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def get_user(self, user_id):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE user_id=$1", user_id)
            return dict(row) if row else None

    async def register_user(self, user_id, full_name, phone, address):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO users(user_id, full_name, phone, address, personal_code, china_code) VALUES($1,$2,$3,$4,$5,$6) "
                "ON CONFLICT (user_id) DO NOTHING",
                user_id, full_name, phone, address, f"C{user_id}", "VXMMM"
            )
            return await self.get_user(user_id)

    async def add_parcel(self, user_id, track_code):
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO parcels(user_id, track_code, status) VALUES($1,$2,'В ожидании')",
                user_id, track_code
            )
            return True

db = DB()
