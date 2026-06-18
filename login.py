import streamlit as st
import pandas as pd


def login_page():

    st.title("🎓 Smart Attendance Mahasiswa")


    nim = st.text_input(
        "NIM Mahasiswa"
    )


    password = st.text_input(
        "Password",
        type="password"
    )


    col1, col2, col3 = st.columns([3, 2, 3])


    with col2:

        if st.button(
            "Login",
            use_container_width=True
        ):

            df = pd.read_csv(
                "data/dataset_absensi_300_mahasiswa.csv"
            )


            data_login = df[
                (df["NIM"].astype(str) == nim)
                &
                (df["Password"] == password)
            ]


            if not data_login.empty:

                st.session_state.login = True

                st.session_state.nim = nim

                st.session_state.nama = (
                    data_login.iloc[0]["Nama"]
                )


                st.success(
                    "Login berhasil"
                )


                st.rerun()


            else:

                st.error(
                    "NIM atau password salah"
                )