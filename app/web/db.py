import os
import sqlite3
import time
import cv2

class LogStore:
    def __init__(self, db_path=os.getenv("DATABASE_PATH", "smart_cctv.db")):
        self.db_path = db_path
        self.screenshot_dir = os.path.abspath("data/screenshots")
        self._init()

    def _init(self):
        os.makedirs(self.screenshot_dir, exist_ok=True)
        with sqlite3.connect(self.db_path) as con:
            con.execute("""CREATE TABLE IF NOT EXISTS events(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                labels TEXT,
                score REAL,
                image_path TEXT
            );""")

    def log_event(self, labels, score, frame):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        # Use absolute path for storage
        img_filename = f"{int(time.time()*1000)}.jpg"
        img_name = os.path.join(self.screenshot_dir, img_filename)
        cv2.imwrite(img_name, frame)
        
        with sqlite3.connect(self.db_path) as con:
            con.execute("INSERT INTO events(timestamp, labels, score, image_path) VALUES(?,?,?,?)",
                        (ts, ",".join(labels), score, img_name))

    def get_events(self, limit=50):
        with sqlite3.connect(self.db_path) as con:
            cur = con.execute(
                "SELECT id, timestamp, labels, score, image_path FROM events ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cur.fetchall()
        return [{"id": r[0], "timestamp": r[1], "labels": r[2], "score": r[3], "image_path": r[4]} for r in rows]
    
    def get_image_path(self, event_id):
        with sqlite3.connect(self.db_path) as con:
            cur = con.execute("SELECT image_path FROM events WHERE id = ?", (event_id,))
            row = cur.fetchone()
        return row[0] if row else None
    
    def delete_event(self, event_id):
        """Delete a single event and its screenshot"""
        image_path = self.get_image_path(event_id)
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                print(f"✓ Deleted screenshot: {image_path}")
            except Exception as e:
                print(f"✗ Failed to delete screenshot: {e}")
        
        with sqlite3.connect(self.db_path) as con:
            con.execute("DELETE FROM events WHERE id = ?", (event_id,))
        print(f"✓ Deleted log entry: {event_id}")
    
    def delete_old_events(self, days=7):
        """Delete events older than specified days and their screenshots"""
        import datetime
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
        
        with sqlite3.connect(self.db_path) as con:
            cur = con.execute(
                "SELECT id, image_path FROM events WHERE timestamp < ? ORDER BY id DESC",
                (cutoff_str,)
            )
            old_events = cur.fetchall()
        
        deleted_count = 0
        for event_id, image_path in old_events:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"✗ Failed to delete screenshot: {e}")
            
            with sqlite3.connect(self.db_path) as con:
                con.execute("DELETE FROM events WHERE id = ?", (event_id,))
            deleted_count += 1
        
        return deleted_count
    
    def delete_unavailable_screenshots(self):
        """Delete database entries for missing screenshot files"""
        with sqlite3.connect(self.db_path) as con:
            cur = con.execute("SELECT id, image_path FROM events")
            all_events = cur.fetchall()
        
        deleted_count = 0
        for event_id, image_path in all_events:
            if image_path and not os.path.exists(image_path):
                with sqlite3.connect(self.db_path) as con:
                    con.execute("DELETE FROM events WHERE id = ?", (event_id,))
                print(f"✓ Removed unavailable entry: ID {event_id} ({image_path})")
                deleted_count += 1
        
        return deleted_count
    
    def clear_all_logs(self):
        """Clear all logs and screenshots (WARNING: Destructive operation)"""
        with sqlite3.connect(self.db_path) as con:
            cur = con.execute("SELECT image_path FROM events")
            all_images = cur.fetchall()
        
        # Delete all screenshot files
        for (image_path,) in all_images:
            if image_path and os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"✗ Failed to delete: {e}")
        
        # Delete all database entries
        with sqlite3.connect(self.db_path) as con:
            con.execute("DELETE FROM events")
        
        print(f"✓ All {len(all_images)} logs and screenshots cleared")
