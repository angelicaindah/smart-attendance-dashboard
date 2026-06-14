import streamlit as st
import pandas as pd

from login import login_page



st.set_page_config(

    page_title="Smart Attendance Dashboard",

    page_icon="🎓",

    layout="wide"

)



# cek login

if "login" not in st.session_state:

    st.session_state.login = False



# ===================
# LOGIN PAGE
# ===================

if st.session_state.login == False:


    login_page()



# ===================
# DASHBOARD
# ===================

else:


    st.title(
        "🎓 Smart Attendance Dashboard"
    )


    # ambil data

    df = pd.read_csv(
        "data/dataset_absensi_50_mahasiswa.csv"
    )



    # ambil data mahasiswa yang login

    mahasiswa = df[
        df["NIM"].astype(str)
        ==
        st.session_state.nim
    ]



    if not mahasiswa.empty:


        nama = mahasiswa.iloc[0]["Nama"]


        st.success(
            f"Halo, {nama} 👋"
        )


    st.divider()



    # statistik

    st.subheader(
        "📊 Statistik Kehadiran"
    )



    col1, col2, col3 = st.columns(3)



    with col1:

        st.metric(
            "Jumlah Mahasiswa",
            len(df)
        )


    with col2:

        rata = round(
            df["Persentase_Hadir"].mean(),
            2
        )

        st.metric(
            "Rata-rata Kehadiran",
            f"{rata}%"
        )



    with col3:

        tinggi = df["Persentase_Hadir"].max()

        st.metric(
            "Kehadiran Tertinggi",
            f"{tinggi}%"
        )



    st.divider()



    # tampil data

    st.subheader(
        "👨‍🎓 Data Absensi Mahasiswa"
    )


    st.dataframe(
        df,
        use_container_width=True
    )



    st.divider()



    # grafik

    st.subheader(
        "📈 Grafik Kehadiran"
    )


    st.bar_chart(

        df.set_index("Nama")
        ["Persentase_Hadir"]

    )



    st.divider()



    # logout

    col1, col2, col3 = st.columns([3,2,3])


    with col2:


        if st.button(
            "Logout",
            use_container_width=True
        ):


            st.session_state.login = False

            st.rerun()