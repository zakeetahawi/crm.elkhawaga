import sqlite3

DB_PATH = 'db.sqlite3'
TABLE = 'accounts_companyinfo'  # قد يكون اسم الجدول بهذا الشكل حسب Django
COLUMN_TO_REMOVE = 'social_links'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# احصل على جميع الأعمدة الحالية
cursor.execute(f'PRAGMA table_info({TABLE})')
columns = [row[1] for row in cursor.fetchall() if row[1] != COLUMN_TO_REMOVE]
columns_str = ', '.join(columns)

# أنشئ جدولاً مؤقتاً بدون العمود المكرر
cursor.execute(f"CREATE TABLE {TABLE}_new AS SELECT {columns_str} FROM {TABLE}")

# احذف الجدول القديم
cursor.execute(f"DROP TABLE {TABLE}")

# أعد تسمية الجدول المؤقت للاسم الأصلي
cursor.execute(f"ALTER TABLE {TABLE}_new RENAME TO {TABLE}")

conn.commit()
conn.close()

print(f"تم حذف العمود {COLUMN_TO_REMOVE} بنجاح من الجدول {TABLE}.")
