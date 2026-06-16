import pandas as pd
import streamlit as st
from login import login_page

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

import os
import time
import io
import qrcode
from datetime import datetime


FILE_RIWAYAT = "data/riwayat_absen.csv"
FILE_FEEDBACK = "data/data_feedback.csv"

def simpan_scan_qr(nim):
    # Memastikan folder 'data' ada
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # Buat data baru
    data_baru = pd.DataFrame({
        "NIM": [nim],
        # Perhatikan di sini: langsung panggil datetime.now()
        "Waktu_Absen": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Status": ["Hadir"]
    })
    
    # Simpan (append) ke file CSV
    data_baru.to_csv(FILE_RIWAYAT, mode='a', index=False, header=not os.path.exists(FILE_RIWAYAT))

# =========================
# SETTING HALAMAN
# =========================

st.set_page_config(
    page_title="Smart Attendance Dashboard",
    page_icon="🎓",
    layout="wide"
)



# =========================
# INISIALISASI FILE
# =========================

def inisialisasi_file_riwayat():

    if not os.path.exists("data"):
        os.makedirs("data")


    if not os.path.exists(FILE_RIWAYAT):

        df_kosong = pd.DataFrame(
            columns=[
                "NIM",
                "Nama",
                "Waktu_Absen",
                "Status"
            ]
        )


        df_kosong.to_csv(
            FILE_RIWAYAT,
            index=False
        )



inisialisasi_file_riwayat()



if not os.path.exists("data"):
    os.makedirs("data")



if not os.path.exists(FILE_FEEDBACK):

    pd.DataFrame(
        columns=[
            "NIM",
            "Feedback"
        ]
    ).to_csv(
        FILE_FEEDBACK,
        index=False
    )



# =========================
# FUNGSI FEEDBACK
# =========================

def simpan_feedback(nim, status):

    df_fb = pd.read_csv(FILE_FEEDBACK)


    df_fb = df_fb[
        df_fb["NIM"].astype(str) != str(nim)
    ]


    data_baru = pd.DataFrame(
        [
            {
                "NIM": str(nim),
                "Feedback": status
            }
        ]
    )


    df_fb = pd.concat(
        [
            df_fb,
            data_baru
        ],
        ignore_index=True
    )


    df_fb.to_csv(
        FILE_FEEDBACK,
        index=False
    )



# =========================
# FUNGSI RIWAYAT ABSEN
# =========================

def tambah_ke_riwayat(nim, nama):

    waktu = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    data_baru = pd.DataFrame(
        [
            {
                "NIM": str(nim),
                "Nama": nama,
                "Waktu_Absen": waktu,
                "Status": "Hadir"
            }
        ]
    )


    data_baru.to_csv(
        FILE_RIWAYAT,
        mode="a",
        header=False,
        index=False
    )



# =========================
# QR CODE
# =========================

def generate_qr(data):

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )


    qr.add_data(data)


    qr.make(
        fit=True
    )


    img = qr.make_image(
        fill_color="black",
        back_color="white"
    )


    buffer = io.BytesIO()


    img.save(buffer)


    return buffer



# =========================
# SESSION LOGIN
# =========================

if "login" not in st.session_state:

    st.session_state.login = False



if "nim" not in st.session_state:

    st.session_state.nim = ""



if "nama" not in st.session_state:

    st.session_state.nama = ""



# =========================
# ABSENSI VIA QR
# =========================

query_params = st.query_params



if "nim" in query_params:

    nim_dari_qr = query_params["nim"]


    tambah_ke_riwayat(
        nim_dari_qr,
        "Mahasiswa via QR"
    )


    st.success(
        f"✅ Absensi berhasil tercatat untuk NIM: {nim_dari_qr}!"
    )


    time.sleep(2)


    st.rerun()



# =========================
# LOGIN PAGE
# =========================

if st.session_state.login == False:

    login_page()

# =========================
# DASHBOARD
# =========================

else:


    df = pd.read_csv(
        "data/dataset_absensi_50_mahasiswa.csv"
    )


    total_pertemuan = 20



    # =========================
    # UPDATE DATA ABSENSI QR
    # =========================

    if os.path.exists(FILE_RIWAYAT):

        df_riwayat = pd.read_csv(
            FILE_RIWAYAT
        )


        if not df_riwayat.empty:


            hitungan_absen = (
                df_riwayat
                .groupby("NIM")["Status"]
                .count()
                .reset_index()
            )


            for index, row in df.iterrows():


                nim = str(row["NIM"])


                if nim in hitungan_absen["NIM"].astype(str).values:


                    tambahan = (
                        hitungan_absen[
                            hitungan_absen["NIM"].astype(str) == nim
                        ]["Status"]
                        .values[0]
                    )


                    df.at[index, "Hadir"] = (
                        int(row["Hadir"])
                        +
                        int(tambahan)
                    )


                    df.at[index, "Persentase_Hadir"] = round(
                        (
                            df.at[index, "Hadir"]
                            /
                            total_pertemuan
                        )
                        *
                        100,
                        2
                    )



    # =========================
    # JUDUL DASHBOARD
    # =========================

    st.title(
        "🎓 Smart Attendance Dashboard"
    )



    nama_mahasiswa = (
        df[
            df["NIM"].astype(str)
            ==
            str(st.session_state.nim)
        ]["Nama"]
        .values[0]
    )



    st.subheader(
        f"Hai, {nama_mahasiswa}! 👋"
    )



    # =========================
    # TABEL ABSENSI
    # =========================

    terakhir_absen = (

        pd.read_csv(FILE_RIWAYAT)
        .drop_duplicates(
            subset=["NIM"],
            keep="last"
        )[["NIM", "Status"]]

        if os.path.exists(FILE_RIWAYAT)

        else

        pd.DataFrame(
            columns=[
                "NIM",
                "Status"
            ]
        )
    )



    df_tampil = df[
        [
            "NIM",
            "Nama"
        ]
    ].copy()



    df_tampil = (
        df_tampil
        .merge(
            terakhir_absen,
            on="NIM",
            how="left"
        )
        .fillna("Belum Absen")
    )



    df_tampil.insert(
        0,
        "No",
        range(
            1,
            len(df_tampil)+1
        )
    )



    df_tampil.rename(
        columns={
            "Status":"Absensi"
        },
        inplace=True
    )



    st.subheader(
        "👨‍🎓 Data Absensi Mahasiswa"
    )



    st.dataframe(
        df_tampil,
        use_container_width=True,
        hide_index=True
    )



    # =========================
    # QR CODE
    # =========================

    st.divider()



    st.subheader(
        "📷 Absensi QR Code"
    )



    st.write(
        "Silakan scan QR Code di bawah ini untuk melakukan absensi."
    )



    col_kiri, col_tengah, col_kanan = st.columns(
        [1,2,1]
    )



    with col_tengah:


        data_qr = (
            f"http://192.168.18.18:8501/"
            f"?nim={st.session_state.nim}"
        )


        qr_img = generate_qr(
            data_qr
        )


        st.image(
            qr_img,
            caption=f"QR Code untuk NIM: {st.session_state.nim}",
            width=250
        )



    # =========================
    # STATISTIK KEHADIRAN PERSONAL
    # =========================

    st.subheader(
        "📈 Statistik Kehadiran Anda"
    )



    if os.path.exists(FILE_RIWAYAT):


        df_riwayat = pd.read_csv(
            FILE_RIWAYAT
        )



        absen_mahasiswa = df_riwayat[
            df_riwayat["NIM"].astype(str)
            ==
            str(st.session_state.nim)
        ]



        jumlah_scan_baru = len(
            absen_mahasiswa
        )



        mask = (
            df["NIM"].astype(str)
            ==
            str(st.session_state.nim)
        )



        if mask.any():


            data_asli = df[mask].iloc[0]



            hadir_dasar = int(
                data_asli["Hadir"]
            )



            total_hadir = (
                hadir_dasar
                +
                jumlah_scan_baru
            )



            persentase_final = round(
                (
                    total_hadir
                    /
                    20
                )
                *
                100,
                2
            )



            col_m1, col_m2, col_m3 = st.columns(3)



            col_m1.metric(
                "Kehadiran",
                f"{total_hadir}x"
            )



            col_m2.metric(
                "Alpha",
                f"{data_asli['Izin'] + data_asli['Sakit']}x"
            )



            col_m3.metric(
                "Persentase",
                f"{persentase_final}%"
            )



            if not absen_mahasiswa.empty:


                st.bar_chart(
                    absen_mahasiswa
                    .set_index("Waktu_Absen")[["Status"]]
                )


            else:


                st.info(
                    "Belum ada riwayat scan QR."
                )


        else:


            st.error(
                "Data NIM tidak ditemukan di database utama."
            )


    else:


        st.info(
            "Belum ada data riwayat."
        )
        # =========================
    # K-MEANS CLUSTERING
    # =========================

    st.subheader(
        "🤖 Analisis Pengelompokan Mahasiswa (K-Means)"
    )


    kolom_X = "Hadir"

    kolom_Y = "Persentase_Hadir"



    if (
        kolom_X in df.columns
        and
        kolom_Y in df.columns
    ):


        X = df[
            [
                kolom_X,
                kolom_Y
            ]
        ]



        kmeans = KMeans(
            n_clusters=3,
            random_state=42
        )



        df["Cluster"] = kmeans.fit_predict(
            X
        )



        cluster_means = (
            df.groupby("Cluster")[kolom_Y]
            .mean()
            .sort_values(
                ascending=False
            )
        )



        labels = {}



        status_kategori = [

            "Sangat Rajin (High)",

            "Cukup Rajin (Medium)",

            "Butuh Perhatian (Low)"

        ]



        for i, cluster_id in enumerate(
            cluster_means.index
        ):


            labels[cluster_id] = status_kategori[i]



        df["Kategori"] = (
            df["Cluster"]
            .map(labels)
        )



        col_grafik, col_txt = st.columns(
            [2,1]
        )



        with col_grafik:


            fig, ax = plt.subplots(
                figsize=(10,5)
            )



            ax.scatter(

                df[kolom_X],

                df[kolom_Y],

                c=df["Cluster"],

                s=100

            )



            ax.set_title(
                "Visualisasi Kelompok Kehadiran Mahasiswa"
            )


            ax.set_xlabel(
                "Jumlah Kehadiran"
            )


            ax.set_ylabel(
                "Persentase Kehadiran (%)"
            )


            ax.grid(
                True
            )


            st.pyplot(
                fig
            )



        with col_txt:


            st.write(
                "### 💡 Penjelasan Kelompok"
            )


            st.write(
                "Hasil algoritma K-Means membagi mahasiswa menjadi 3 kategori:"
            )



            for cluster_id, nama_kat in labels.items():


                if "Sangat" in nama_kat:


                    st.success(
                        nama_kat
                    )


                elif "Cukup" in nama_kat:


                    st.warning(
                        nama_kat
                    )


                else:


                    st.error(
                        nama_kat
                    )



            st.info(
                "Kategori ditentukan otomatis berdasarkan pola kehadiran."
            )



    else:


        st.error(
            f"Gagal memproses K-Means. Pastikan kolom {kolom_X} dan {kolom_Y} tersedia."
        )



    # =========================
    # FITUR PENCARIAN DATA
    # =========================

    st.divider()


    st.subheader(
        "🔍 Cari Data atau Simulasi Kehadiran"
    )



    col_a, col_b = st.columns(2)



    with col_a:

        cari_nama = st.text_input(
            "Nama Mahasiswa:"
        )



    with col_b:

        input_hadir = st.number_input(
            "Jumlah Hadir (Opsional):",
            min_value=0,
            value=0,
            step=1
        )



    if st.button(
        "Proses Data"
    ):


        if cari_nama:


            df_hasil = df[
                df["Nama"]
                .str.contains(
                    cari_nama,
                    case=False,
                    na=False
                )
            ]



            if not df_hasil.empty:


                data_asli = df_hasil.iloc[0]



                st.write(
                    f"Ditemukan data untuk: **{data_asli['Nama']}**"
                )



                st.dataframe(
                    df_hasil[
                        [
                            "Nama",
                            "Hadir",
                            "Persentase_Hadir",
                            "Kategori"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )



            else:


                st.warning(
                    "Nama mahasiswa tidak ditemukan."
                )



        else:


            st.error(
                "Silakan masukkan nama mahasiswa terlebih dahulu."
            )



    # =========================
    # FEEDBACK MAHASISWA
    # =========================

    st.divider()


    st.subheader(
        "📝 Feedback Penggunaan Web"
    )



    df_baca_fb = pd.read_csv(
        FILE_FEEDBACK
    )



    jml_puas = len(
        df_baca_fb[
            df_baca_fb["Feedback"] == "Puas"
        ]
    )



    jml_kurang = len(
        df_baca_fb[
            df_baca_fb["Feedback"] == "Kurang Puas"
        ]
    )



    jml_gangguan = len(
        df_baca_fb[
            df_baca_fb["Feedback"] == "Banyak Gangguan"
        ]
    )



    st.info(
        f"📊 Statistik Saat Ini: 👍 Puas: {jml_puas} | 😢 Kurang Puas: {jml_kurang} | 😡 Banyak Gangguan: {jml_gangguan}"
    )



    st.write(
        "Bagaimana pengalaman kamu mengakses web ini hari ini?"
    )



    col_fb1, col_fb2, col_fb3 = st.columns(3)



    with col_fb1:


        if st.button(
            "Puas 👍",
            use_container_width=True
        ):


            simpan_feedback(
                st.session_state.nim,
                "Puas"
            )


            st.success(
                "Terima kasih! Senang web berjalan lancar."
            )



    with col_fb2:


        if st.button(
            "Kurang Puas 😢",
            use_container_width=True
        ):


            simpan_feedback(
                st.session_state.nim,
                "Kurang Puas"
            )


            st.warning(
                "Terima kasih atas feedback."
            )



    with col_fb3:


        if st.button(
            "Banyak Gangguan 😡",
            use_container_width=True
        ):


            simpan_feedback(
                st.session_state.nim,
                "Banyak Gangguan"
            )


            st.error(
                "Mohon maaf atas kendalanya."
            )



    # =========================
    # LOGOUT
    # =========================

    st.divider()



    col1, col2, col3 = st.columns(
        [3,2,3]
    )



    with col2:


        if st.button(
            "Logout",
            use_container_width=True
        ):


            st.session_state.login = False

            st.session_state.nim = ""

            st.session_state.nama = ""


            st.rerun()