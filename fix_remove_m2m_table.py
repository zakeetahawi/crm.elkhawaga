import sqlite3

DB_PATH = 'db.sqlite3'
TABLE = 'accounts_notification_target_users'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute(f"DROP TABLE IF EXISTS {TABLE}")
    print(f"تم حذف الجدول {TABLE} بنجاح.")
except Exception as e:
    print(f"حدث خطأ أثناء حذف الجدول: {e}")
finally:
    conn.commit()
    conn.close()
