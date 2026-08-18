import hashlib

import streamlit as st

from database import (
    Session,
    User,
)


# =================================
# Password
# =================================

def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# =================================
# Role Helpers
# =================================

def get_current_user():

    username = st.session_state.get(
        "username"
    )

    if not username:
        return None

    db = Session()

    try:

        user = (
            db.query(User)
            .filter(
                User.username == username,
                User.active == 1
            )
            .first()
        )

        return user

    finally:

        db.close()


def get_current_role():

    user = get_current_user()

    if not user:
        return None

    return str(
        user.role or ""
    ).upper()


def is_admin():

    return (
        get_current_role()
        ==
        "ADMIN"
    )


def is_editor():

    return get_current_role() in (
        "ADMIN",
        "TM",
    )


def is_viewer():

    return (
        get_current_role()
        ==
        "VIEWER"
    )


# =================================
# Login
# =================================

def check_login():

    if st.session_state.get(
        "authenticated",
        False
    ):
        return True

    st.title(
        "🔐 MGPM Price Monitor"
    )

    st.subheader(
        "Login"
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Login",
        type="primary",
        use_container_width=True
    ):

        db = Session()

        try:

            user = (
                db.query(User)
                .filter(
                    User.username == username,
                    User.active == 1
                )
                .first()
            )

            if (
                user
                and
                user.password_hash
                ==
                hash_password(password)
            ):

                st.session_state[
                    "authenticated"
                ] = True

                st.session_state[
                    "username"
                ] = user.username

                st.session_state[
                    "role"
                ] = user.role

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

        finally:

            db.close()

    return False


# =================================
# Logout
# =================================

def logout():

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state[
            "authenticated"
        ] = False

        st.session_state.pop(
            "username",
            None
        )

        st.session_state.pop(
            "role",
            None
        )

        st.rerun()


# =================================
# User Information
# =================================

def show_user_info():

    username = st.session_state.get(
        "username",
        "-"
    )

    role = st.session_state.get(
        "role",
        "-"
    )

    st.sidebar.caption(
        f"👤 {username}"
    )

    st.sidebar.caption(
        f"🔑 Role: {role}"
    )


# =================================
# Settings Page
# =================================

def settings_page():

    st.header(
        "⚙️ Settings"
    )

    # =================================
    # Current User
    # =================================

    current_user = (
        get_current_user()
    )

    if current_user:

        st.subheader(
            "👤 Current User"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Username:** "
                f"{current_user.username}"
            )

        with col2:

            st.write(
                f"**Role:** "
                f"{str(current_user.role).upper()}"
            )

    st.divider()

    # =================================
    # Admin Only
    # =================================

    if not is_admin():

        st.info(
            "사용자 관리는 ADMIN 권한에서만 "
            "사용할 수 있습니다."
        )

        return

    st.subheader(
        "👥 User Management"
    )

    db = Session()

    try:

        users = (
            db.query(User)
            .order_by(
                User.username
            )
            .all()
        )

        # =================================
        # Existing Users
        # =================================

        if users:

            rows = []

            for user in users:

                rows.append(
                    {
                        "Username":
                            user.username,

                        "Role":
                            str(
                                user.role or ""
                            ).upper(),

                        "Active":
                            bool(
                                user.active
                            ),
                    }
                )

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "등록된 사용자가 없습니다."
            )

        st.divider()

        # =================================
        # Add User
        # =================================

        st.subheader(
            "➕ Add User"
        )

        with st.form(
            "add_user_form",
            clear_on_submit=True
        ):

            new_username = st.text_input(
                "Username"
            )

            new_password = st.text_input(
                "Password",
                type="password"
            )

            new_role = st.selectbox(
                "Role",
                [
                    "ADMIN",
                    "TM",
                    "VIEWER",
                ]
            )

            add_user = (
                st.form_submit_button(
                    "사용자 추가"
                )
            )

            if add_user:

                username = (
                    new_username
                    .strip()
                )

                if not username:

                    st.error(
                        "Username을 입력하세요."
                    )

                elif not new_password:

                    st.error(
                        "Password를 입력하세요."
                    )

                else:

                    existing = (
                        db.query(User)
                        .filter(
                            User.username
                            ==
                            username
                        )
                        .first()
                    )

                    if existing:

                        st.error(
                            "이미 존재하는 Username입니다."
                        )

                    else:

                        new_user = User(
                            username=username,
                            password_hash=(
                                hash_password(
                                    new_password
                                )
                            ),
                            role=new_role,
                            active=1,
                        )

                        db.add(
                            new_user
                        )

                        db.commit()

                        st.success(
                            f"사용자 "
                            f"'{username}' "
                            f"추가 완료"
                        )

                        st.rerun()

        # =================================
        # Password Change
        # =================================

        st.divider()

        st.subheader(
            "🔑 Change Password"
        )

        password_users = [
            user.username
            for user in users
        ]

        if password_users:

            selected_username = (
                st.selectbox(
                    "사용자",
                    password_users,
                    key="password_user"
                )
            )

            new_password = st.text_input(
                "새 Password",
                type="password",
                key="new_password"
            )

            if st.button(
                "Password 변경",
                key="change_password"
            ):

                if not new_password:

                    st.error(
                        "새 Password를 입력하세요."
                    )

                else:

                    target_user = (
                        db.query(User)
                        .filter(
                            User.username
                            ==
                            selected_username
                        )
                        .first()
                    )

                    if target_user:

                        target_user.password_hash = (
                            hash_password(
                                new_password
                            )
                        )

                        db.commit()

                        st.success(
                            "Password 변경 완료"
                        )

                        st.rerun()

    finally:

        db.close()