import sqlite3


db = "price_monitor.db"


conn = sqlite3.connect(db)

cursor = conn.cursor()


try:

    cursor.execute(
        """
        ALTER TABLE products
        ADD COLUMN monitoring INTEGER DEFAULT 1
        """
    )

    conn.commit()

    print("monitoring 컬럼 추가 완료")


except Exception as e:

    print("오류:", e)


finally:

    conn.close()