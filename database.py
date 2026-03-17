def get_parcels(self, client_code):
    cursor = self.conn.execute(
        "SELECT * FROM parcels WHERE client_code=? ORDER BY created_at DESC",
        (client_code,)
    )
    return [dict(row) for row in cursor.fetchall()]

def get_all_users(self):
    cursor = self.conn.execute(
        "SELECT * FROM users ORDER BY created_at DESC"
    )
    return [dict(row) for row in cursor.fetchall()]

def add_parcel(self, client_code, track_number, description, weight, status):
    with self.lock:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            """INSERT INTO parcels 
            (client_code, track_number, description, weight, status, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?)""",
            (client_code, track_number, description, weight, status, now, now)
        )
        self.conn.commit()
