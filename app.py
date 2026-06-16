import pandas as pd
import streamlit as st
from login import login_page

import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

import os
import io
import qrcode
from datetime import datetime

FILE_RIWAYAT = "data/riwayat_absen.csv"
FILE_FEEDBACK = "data/data_feedback.csv"

    # =========================
    # SETTING HALAMAN
    # =========================

st.set_page_config(
    page_title="Smart Attendance",
    page_icon="🎓",
    layout="wide"
)

    # =========================
    #    INISIALISASI FILE
    # =========================

def inisialisasi_file_riwayat():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    if not os.path.exists(FILE_RIWAYAT):
        df_kosong = pd.DataFrame(columns=["NIM", "Nama", "Waktu_Absen", "Status"])
        df_kosong.to_csv(FILE_RIWAYAT, index=False)

    inisialisasi_file_riwayat()

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(FILE_FEEDBACK):
    pd.DataFrame(columns=["NIM", "Feedback"]).to_csv(FILE_FEEDBACK, index=False)

    # =========================
    # FUNGSI RIWAYAT ABSEN
    # =========================

def tambah_ke_riwayat(nim, nama):
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_baru = pd.DataFrame([{
        "NIM": str(nim),
        "Nama": nama,
        "Waktu_Absen": waktu,
        "Status": "Hadir"
    }])
    
    header = not os.path.exists(FILE_RIWAYAT) or os.path.getsize(FILE_RIWAYAT) == 0
    data_baru.to_csv(FILE_RIWAYAT, mode="a", header=header, index=False)

    #     =========================
    # QR CODE
    # =========================

def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer)
    return buffer

    # =========================
    # SESSION STATE
    # =========================

if "login" not in st.session_state:
    st.session_state.login = False

if "nim" not in st.session_state:
    st.session_state.nim = ""

if "nama" not in st.session_state:
    st.session_state.nama = ""

    # =========================
    # ABSENSI VIA QR (Tanpa Login)
    # =========================

query_params = st.query_params

if "nim" in query_params:
    # Halaman QR scan (tidak perlu login)
    st.title("📷 Absensi QR Code")
    
    nim_dari_qr = query_params["nim"]
    
    # Cek apakah mahasiswa ada di database
    df_mahasiswa = pd.read_csv("data/dataset_absensi_50_mahasiswa.csv")
    mahasiswa = df_mahasiswa[df_mahasiswa["NIM"].astype(str) == str(nim_dari_qr)]
    
    if not mahasiswa.empty:
        nama_mahasiswa = mahasiswa["Nama"].values[0]
        tambah_ke_riwayat(nim_dari_qr, nama_mahasiswa)
        
        waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"✅ **Absensi berhasil tercatat!**\n\nNIM: {nim_dari_qr}\nNama: {nama_mahasiswa}\nWaktu: {waktu}")
        st.info("Silakan tutup halaman ini atau kembali ke kelas.")
        
        # Tambah tombol untuk login dan lihat statistik
        st.divider()
        st.subheader("📊 Lihat Statistik Kehadiran Anda")
        if st.button("Login untuk Lihat Statistik"):
            st.session_state.login = False
            st.session_state.nim = nim_dari_qr
            st.session_state.nama = nama_mahasiswa
            st.rerun()
    else:
        st.error("❌ **NIM tidak terdaftar!**\n\nSilakan hubungi dosen/pemandu.")
    
    st.stop()  # Stop here, tidak lanjut ke dashboard

    # =========================
    #   LOGIN PAGE
    # =========================

if st.session_state.login == False:
    login_page()
    st.stop()

    # =========================
    # DASHBOARD MAHASISWA
    # =========================

st.title("🎓 Smart Attendance Dashboard")

df_mahasiswa = pd.read_csv("data/dataset_absensi_50_mahasiswa.csv")
mahasiswa = df_mahasiswa[df_mahasiswa["NIM"].astype(str) == str(st.session_state.nim)]

if not mahasiswa.empty:
    nama_mahasiswa = mahasiswa["Nama"].values[0]
    st.subheader(f"Hai, {nama_mahasiswa}! 👋")
    
    # Statistik Personal
    st.subheader("📈 Statistik Kehadiran Anda")
    
    if os.path.exists(FILE_RIWAYAT):
        df_riwayat = pd.read_csv(FILE_RIWAYAT)
        absen_mahasiswa = df_riwayat[df_riwayat["NIM"].astype(str) == str(st.session_state.nim)]
        jumlah_hadir = len(absen_mahasiswa)
        
        hadir_dasar = int(mahasiswa["Hadir"].values[0])
        total_hadir = hadir_dasar + jumlah_hadir
        persentase_final = round((total_hadir / 20) * 100, 2)
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Kehadiran", f"{total_hadir}x")
        col_m2.metric("Alpha", f"{mahasiswa['Izin'].values[0] + mahasiswa['Sakit'].values[0]}x")
        col_m3.metric("Persentase", f"{persentase_final}%")
        
        if not absen_mahasiswa.empty:
            st.bar_chart(absen_mahasiswa.set_index("Waktu_Absen")[["Status"]])
        else:
            st.info("Belum ada riwayat scan QR.")
    else:
        st.info("Belum ada data riwayat.")
    
    # QR Code untuk Absen
    st.divider()
    st.subheader("📷 Absensi QR Code")
    st.write("Scan QR Code ini untuk absen:")
    
    # ✅ GANTI URL INI DENGAN URL STREAMLIT CLOUD Kamu
    streamlit_url = "https://smart-attendance-dashboard-angelicaindah.streamlit.app/app"
    data_qr = f"{streamlit_url}?nim={st.session_state.nim}"
    
    qr_img = generate_qr(data_qr)
    st.image(qr_img, caption=f"QR Code untuk NIM: {st.session_state.nim}", width=250)
    
    # =========================
    # TABEL DATA MAHASISWA (UPDATE MANUAL)
    # =========================
    
    st.divider()
    st.subheader("👨‍🎓 Data Absensi Semua Mahasiswa")
    
    # ✅ Button Refresh Data (Manual)
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # ✅ Baca CSV riwayat terbaru setiap kali dashboard dibuka atau refresh
    if os.path.exists(FILE_RIWAYAT):
        df_riwayat = pd.read_csv(FILE_RIWAYAT)
    else:
        df_riwayat = pd.DataFrame(columns=["NIM", "Nama", "Waktu_Absen", "Status"])
    
    # ✅ Hitung jumlah absen per NIM
    hitungan_absen = df_riwayat.groupby("NIM")["Status"].count().reset_index()
    hitungan_absen.rename(columns={"Status": "Jumlah_Hadir"}, inplace=True)
    
    # ✅ Update dataframe utama dengan data absen terbaru
    df_tampil = df_mahasiswa[["NIM", "Nama"]].copy()
    
    # ✅ Merge dengan hitungan absen
    df_tampil = df_tampil.merge(hitungan_absen, on="NIM", how="left")
    df_tampil["Jumlah_Hadir"] = df_tampil["Jumlah_Hadir"].fillna(0)
    
    # ✅ Tentukan status: "Hadir" jika sudah absen 1x+, "Belum Absen" jika 0
    df_tampil["Status"] = df_tampil["Jumlah_Hadir"].apply(lambda x: "Hadir" if x > 0 else "Belum Absen")
    
    # ✅ Sortir berdasarkan jumlah hadir (terbesar di atas)
    df_tampil = df_tampil.sort_values(by="Jumlah_Hadir", ascending=False)
    
    # ✅ Add kolom No
    df_tampil.insert(0, "No", range(1, len(df_tampil)+1))
    
    # ✅ Rename kolom
    df_tampil.rename(columns={
        "Jumlah_Hadir": "Jumlah Hadir",
        "Status": "Absensi"
    }, inplace=True)
    
    # ✅ Tampilkan tabel
    st.dataframe(
        df_tampil,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Absensi": {
                "width": 120
            }
        }
    )
    
    # ✅ Highlight mahasiswa yang sudah absen
    st.success(f"✅ Total mahasiswa yang sudah absen: {len(df_tampil[df_tampil['Absensi'] == 'Hadir'])} dari {len(df_tampil)}")
    
    # K-Means Clustering (opsional)
    st.divider()
    st.subheader("🤖 Analisis Pengelompokan Mahasiswa (K-Means)")
    
    df = df_mahasiswa.copy()
    total_pertemuan = 20
    
    # Update data absensi QR ke dataframe
    for index, row in df.iterrows():
        nim = str(row["NIM"])
        if nim in hitungan_absen["NIM"].astype(str).values:
            tambahan = hitungan_absen[hitungan_absen["NIM"].astype(str) == nim]["Jumlah_Hadir"].values[0]
            df.at[index, "Hadir"] = int(row["Hadir"]) + int(tambahan)
            df.at[index, "Persentase_Hadir"] = round((df.at[index, "Hadir"] / total_pertemuan) * 100, 2)
    
    kolom_X = "Hadir"
    kolom_Y = "Persentase_Hadir"
    
    if kolom_X in df.columns and kolom_Y in df.columns:
        X = df[[kolom_X, kolom_Y]]
        kmeans = KMeans(n_clusters=3, random_state=42)
        df["Cluster"] = kmeans.fit_predict(X)
        
        cluster_means = df.groupby("Cluster")[kolom_Y].mean().sort_values(ascending=False)
        
        labels = {}
        status_kategori = ["Sangat Rajin (High)", "Cukup Rajin (Medium)", "Butuh Perhatian (Low)"]
        
        for i, cluster_id in enumerate(cluster_means.index):
            labels[cluster_id] = status_kategori[i]
        
        df["Kategori"] = df["Cluster"].map(labels)
        
        col_grafik, col_txt = st.columns([2, 1])
        
        with col_grafik:
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.scatter(df[kolom_X], df[kolom_Y], c=df["Cluster"], s=100)
            ax.set_title("Visualisasi Kelompok Kehadiran Mahasiswa")
            ax.set_xlabel("Jumlah Kehadiran")
            ax.set_ylabel("Persentase Kehadiran (%)")
            ax.grid(True)
            st.pyplot(fig)
        
        with col_txt:
            st.write("### 💡 Penjelasan Kelompok")
            st.write("Hasil algoritma K-Means membagi mahasiswa menjadi 3 kategori:")
            
            for cluster_id, nama_kat in labels.items():
                if "Sangat" in nama_kat:
                    st.success(nama_kat)
                elif "Cukup" in nama_kat:
                    st.warning(nama_kat)
                else:
                    st.error(nama_kat)
            
            st.info("Kategori ditentukan otomatis berdasarkan pola kehadiran.")
    
    # Feedback Mahasiswa
    st.divider()
    st.subheader("📝 Feedback Penggunaan Web")
    
    df_baca_fb = pd.read_csv(FILE_FEEDBACK)
    jml_puas = len(df_baca_fb[df_baca_fb["Feedback"] == "Puas"])
    jml_kurang = len(df_baca_fb[df_baca_fb["Feedback"] == "Kurang Puas"])
    jml_gangguan = len(df_baca_fb[df_baca_fb["Feedback"] == "Banyak Gangguan"])
    
    st.info(f"📊 Statistik Saat Ini: 👍 Puas: {jml_puas} | 😢 Kurang Puas: {jml_kurang} | 😡 Banyak Gangguan: {jml_gangguan}")
    
    st.write("Bagaimana pengalaman kamu mengakses web ini hari ini?")
    
    col_fb1, col_fb2, col_fb3 = st.columns(3)
    
    with col_fb1:
        if st.button("Puas 👍", use_container_width=True):
            df_fb = pd.read_csv(FILE_FEEDBACK)
            df_fb = df_fb[df_fb["NIM"].astype(str) != str(st.session_state.nim)]
            data_baru = pd.DataFrame([{"NIM": str(st.session_state.nim), "Feedback": "Puas"}])
            df_fb = pd.concat([df_fb, data_baru], ignore_index=True)
            df_fb.to_csv(FILE_FEEDBACK, index=False)
            st.success("Terima kasih! Senang web berjalan lancar.")
    
    with col_fb2:
        if st.button("Kurang Puas 😢", use_container_width=True):
            df_fb = pd.read_csv(FILE_FEEDBACK)
            df_fb = df_fb[df_fb["NIM"].astype(str) != str(st.session_state.nim)]
            data_baru = pd.DataFrame([{"NIM": str(st.session_state.nim), "Feedback": "Kurang Puas"}])
            df_fb = pd.concat([df_fb, data_baru], ignore_index=True)
            df_fb.to_csv(FILE_FEEDBACK, index=False)
            st.warning("Terima kasih atas feedback.")
    
    with col_fb3:
        if st.button("Banyak Gangguan 😡", use_container_width=True):
            df_fb = pd.read_csv(FILE_FEEDBACK)
            df_fb = df_fb[df_fb["NIM"].astype(str) != str(st.session_state.nim)]
            data_baru = pd.DataFrame([{"NIM": str(st.session_state.nim), "Feedback": "Banyak Gangguan"}])
            df_fb = pd.concat([df_fb, data_baru], ignore_index=True)
            df_fb.to_csv(FILE_FEEDBACK, index=False)
            st.error("Mohon maaf atas kendalanya.")
    
    # Logout
    st.divider()
    if st.button("Logout"):
        st.session_state.login = False
        st.session_state.nim = ""
        st.session_state.nama = ""
        st.rerun()

else:
    st.error("Data NIM tidak ditemukan.")
    if st.button("Logout"):
        st.session_state.login = False
        st.rerun()