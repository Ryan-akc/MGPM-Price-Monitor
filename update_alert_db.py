import sqlite3


conn = sqlite3.connect(
    "price_monitor.db"
)

cursor = conn.cursor()


try:

    cursor.execute(
        """
        ALTER TABLE alerts
        ADD COLUMN viewed_at TEXT
        """
    )

    print("viewed_at added")


except Exception as e:

    print(
        "viewed_at:",
        e
    )



try:

    cursor.execute(
        """
        ALTER TABLE alerts
        ADD COLUMN resolved_at TEXT
        """
    )

    print("resolved_at added")


except Exception as e:

    print(
        "resolved_at:",
        e
    )



conn.commit()

conn.close()


print("DB update complete")