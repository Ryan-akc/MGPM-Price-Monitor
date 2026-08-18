import hashlib

import streamlit as st

from database import Session, User


# =================================
# Password
# =================================

def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# =================================
# User Management
# =================================

def user_management_page():

    st.header("👥 User Management")

    st.caption(
        "Admin 전용 사용자 및 권한 관리"
    )

    db = Session()

    try:

        users = (
            db.query(User)
            .order_by(User.id.asc())
            .all()
        )

        # =================================
        # User List
        # =================================

        st.subheader("Users")

        rows = []

        for user in users:

            rows.append(
                {
                    "ID": user.id,
                    "Username": user.username,
                    "Role": user.role,
                    "Active": (
                        "🟢 Active"
                        if user.active
                        else "🔴 Disabled"
                    ),
                }
            )

        st.dataframe(
            rows,
            use_container_width=True,
            hide_index=True,
            column_config={

                "ID":
                    st.column_config.NumberColumn(
                        "ID",
                        width="small",
                    ),

                "Username":
                    st.column_config.TextColumn(
                        "Username",
                        width="medium",
                    ),

                "Role":
                    st.column_config.TextColumn(
                        "Role",
                        width="medium",
                    ),

                "Active":
                    st.column_config.TextColumn(
                        "Status",
                        width="medium",
                    ),
            },
        )

        st.divider()

        # =================================
        # Select User
        # =================================

        st.subheader(
            "✏️ Edit User"
        )

        if not users:

            st.info(
                "등록된 사용자가 없습니다."
            )

            return

        user_names = [
            user.username
            for user in users
        ]

        selected_username = st.selectbox(
            "User",
            user_names,
        )

        selected_user = next(
            (
                user
                for user in users
                if user.username
                == selected_username
            ),
            None,
        )

        if selected_user is None:

            return

        # =================================
        # Edit Form
        # =================================

        with st.form(
            "edit_user_form"
        ):

            new_password = st.text_input(
                "New Password",
                type="password",
                help=(
                    "비워두면 기존 비밀번호를 "
                    "유지합니다."
                ),
            )

            new_role = st.selectbox(
                "Role",
                [
                    "ADMIN",
                    "TM",
                    "VIEWER",
                ],
                index=[
                    "ADMIN",
                    "TM",
                    "VIEWER",
                ].index(
                    selected_user.role
                    if selected_user.role
                    in (
                        "ADMIN",
                        "TM",
                        "VIEWER",
                    )
                    else "VIEWER"
                ),
            )

            new_active = st.checkbox(
                "Account Active",
                value=bool(
                    selected_user.active
                ),
            )

            save = st.form_submit_button(
                "💾 Save Changes",
                type="primary",
                use_container_width=True,
            )

        if save:

            # -------------------------
            # Password
            # -------------------------

            if new_password.strip():

                selected_user.password_hash = (
                    hash_password(
                        new_password
                    )
                )

            # -------------------------
            # Role
            # -------------------------

            selected_user.role = new_role

            # -------------------------
            # Active
            # -------------------------

            selected_user.active = (
                1
                if new_active
                else 0
            )

            db.commit()

            st.success(
                f"{selected_username} "
                "사용자 정보가 저장되었습니다."
            )

            st.rerun()

        st.divider()

        # =================================
        # Create User
        # =================================

        st.subheader(
            "➕ Create User"
        )

        with st.form(
            "create_user_form"
        ):

            username = st.text_input(
                "Username",
                key="create_username",
            )

            password = st.text_input(
                "Password",
                type="password",
                key="create_password",
            )

            role = st.selectbox(
                "Role",
                [
                    "ADMIN",
                    "TM",
                    "VIEWER",
                ],
                key="create_role",
            )

            create = st.form_submit_button(
                "Create User",
                use_container_width=True,
            )

        if create:

            username = username.strip()

            password = password.strip()

            if not username:

                st.error(
                    "Username을 입력해주세요."
                )

            elif not password:

                st.error(
                    "Password를 입력해주세요."
                )

            else:

                existing = (
                    db.query(User)
                    .filter(
                        User.username
                        == username
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
                                password
                            )
                        ),

                        role=role,

                        active=1,

                    )

                    db.add(new_user)

                    db.commit()

                    st.success(
                        f"{username} "
                        "계정이 생성되었습니다."
                    )

                    st.rerun()

    finally:

        db.close()