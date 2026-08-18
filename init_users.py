import hashlib

from database import (
    Session,
    User,
)


# =================================
# Password Hash
# =================================

def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# =================================
# Users
# =================================

USERS = [

    {
        "username": "Admin",
        "password": "admin1234",
        "role": "ADMIN",
    },

    {
        "username": "TM",
        "password": "tm1234",
        "role": "TM",
    },

    {
        "username": "OVERSEAS",
        "password": "overseas1234",
        "role": "VIEWER",
    },

    {
        "username": "DOMESTIC",
        "password": "domestic1234",
        "role": "VIEWER",
    },

    {
        "username": "MKTg",
        "password": "mktg1234",
        "role": "VIEWER",
    },

]


# =================================
# Create / Update Users
# =================================

def init_users():

    db = Session()

    try:

        for item in USERS:

            username = item["username"]

            user = (
                db.query(User)
                .filter(
                    User.username == username
                )
                .first()
            )

            password_hash = hash_password(
                item["password"]
            )

            if user is None:

                user = User(

                    username=username,

                    password_hash=password_hash,

                    role=item["role"],

                    active=1,

                )

                db.add(user)

                print(
                    f"CREATE: "
                    f"{username} "
                    f"[{item['role']}]"
                )

            else:

                user.password_hash = password_hash

                user.role = item["role"]

                user.active = 1

                print(
                    f"UPDATE: "
                    f"{username} "
                    f"[{item['role']}]"
                )

        db.commit()

        print("")
        print(
            "OK: User initialization completed"
        )

    except Exception as e:

        db.rollback()

        print(
            f"ERROR: {e}"
        )

        raise

    finally:

        db.close()


# =================================
# Main
# =================================

if __name__ == "__main__":

    init_users()