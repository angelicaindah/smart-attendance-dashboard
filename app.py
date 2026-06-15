import pandas as pd
import streamlit as st
from login import login_page

# Tambahkan library untuk clustering dan visualisasi
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import os

# --- LANGKAH 1: PERSIAPAN CATATAN FEEDBACK ---
FILE_FEEDBACK = "data/data_feedback.csv"

# Buat file CSV kosong secara otomatis jika belum ada
if not os.path.exists("data"):
    os.makedirs("data")
if not os.path.exists(FILE_FEEDBACK):
    pd.DataFrame(columns=["NIM", "Feedback"]).to_csv(FILE_FEEDBACK, index=False)

# Fungsi (alat tulis) untuk menyimpan pilihan mahasiswa ke file CSV
def simpan_feedback(nim, status):
    df_fb = pd.read_csv(FILE_FEEDBACK)
    
    # Hapus data lama jika mahasiswa ini sudah pernah memencet tombol sebelumnya
    df_fb = df_fb[df_fb["NIM"].astype(str) != str(nim)]
    
    # Masukkan pilihan baru
    df_baru = pd.DataFrame([{"NIM": str(nim), "Feedback": status}])
    df_fb = pd.concat([df_fb, df_baru], ignore_index=True)
    
    # Simpan kembali ke file CSV
    df_fb.to_csv(FILE_FEEDBACK, index=False)

# Library tambahan untuk menangani timing (digunakan dalam implementasi JS)
import time 

st.set_page_config(
    page_title="Smart Attendance Dashboard", page_icon="🎓", layout="wide"
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
    st.title("🎓 Smart Attendance Dashboard")

    # ambil data
    df = pd.read_csv("data/dataset_absensi_50_mahasiswa.csv")

    # ambil data mahasiswa yang login
    mahasiswa = df[df["NIM"].astype(str) == st.session_state.nim]

    if not mahasiswa.empty:
        nama = mahasiswa.iloc[0]["Nama"]
        st.success(f"Halo, {nama} 👋")

    st.divider()

    # statistik
    st.subheader("📊 Statistik Kehadiran")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Jumlah Mahasiswa", len(df))

    with col2:
        rata = round(df["Persentase_Hadir"].mean(), 2)
        st.metric("Rata-rata Kehadiran", f"{rata}%")

    with col3:
        tinggi = df["Persentase_Hadir"].max()
        st.metric("Kehadiran Tertinggi", f"{tinggi}%")

    st.divider()

    # tampil data
    st.subheader("👨‍🎓 Data Absensi Mahasiswa")
    
    # 1. Pilih kolom yang ingin ditampilkan (Kecualikan 'Password')
    kolom_untuk_ditampilkan = ["NIM", "Nama", "Hadir", "Izin", "Sakit", "Alpha", "Persentase_Hadir"]
    df_tampil = df[kolom_untuk_ditampilkan].copy()
    
    # 2. Ubah index agar dimulai dari 1
    df_tampil.index = range(1, len(df_tampil) + 1)
    
    # 3. Tampilkan ke layar
    st.dataframe(df_tampil, use_container_width=True)

    # grafik bawaan
    st.subheader("📈 Grafik Kehadiran")
    st.bar_chart(df.set_index("Nama")["Persentase_Hadir"])

    st.divider()

    # =========================================================
    # BAGIAN: K-MEANS CLUSTERING & INSIGHT
    # =========================================================
    st.subheader("🤖 Analisis Pengelompokan Mahasiswa (K-Means)")

    kolom_X = "Hadir"
    kolom_Y = "Persentase_Hadir"

    if kolom_X in df.columns and kolom_Y in df.columns:
        X = df[[kolom_X, kolom_Y]]

        # 1. Proses K-Means
        kmeans = KMeans(n_clusters=3, random_state=42)
        df["Cluster"] = kmeans.fit_predict(X)

        # 2. Logika Penjelasan Cluster (Menentukan siapa yang rajin/tidak)
        cluster_means = df.groupby("Cluster")[kolom_Y].mean().sort_values(ascending=False)
        labels = {}
        status_kategori = ["Sangat Rajin (High)", "Cukup Rajin (Medium)", "Butuh Perhatian (Low)"]
        for i, cluster_id in enumerate(cluster_means.index):
            labels[cluster_id] = status_kategori[i]
        
        df["Kategori"] = df["Cluster"].map(labels)

        # 3. Layout Kolom: Kiri (Grafik), Kanan (Penjelasan)
        col_grafik, col_txt = st.columns([2, 1])

        with col_grafik:
            fig, ax = plt.subplots(figsize=(10, 5))
            scatter = ax.scatter(
                df[kolom_X],
                df[kolom_Y],
                c=df["Cluster"],
                cmap="viridis",
                s=100,
                edgecolors="k",
            )
            ax.set_title("Visualisasi Kelompok Kehadiran Mahasiswa", fontsize=14)
            ax.set_xlabel("Jumlah Kehadiran", fontsize=12)
            ax.set_ylabel("Persentase Kehadiran (%)", fontsize=12)
            ax.grid(True, linestyle="--", alpha=0.6)
            st.pyplot(fig)

        with col_txt:
            st.write("### 💡 Penjelasan Kelompok")
            st.write("Hasil algoritma K-Means membagi mahasiswa ke dalam 3 kategori:")
            
            for cluster_id, nama_kat in labels.items():
                if "Sangat" in nama_kat:
                    st.success(f"**{nama_kat}**")
                elif "Cukup" in nama_kat:
                    st.warning(f"**{nama_kat}**")
                else:
                    st.error(f"**{nama_kat}**")
            
            st.info("Kategori ini ditentukan secara otomatis berdasarkan pola kehadiran di dataset.")
    else:
        st.error(f"Gagal memproses K-Means. Pastikan kolom '{kolom_X}' dan '{kolom_Y}' tersedia.")

    st.divider()
    
# # --- FITUR PENCARIAN & VERIFIKASI DATA ---
    st.subheader("🔍 Cari Data atau Simulasi Kehadiran")
    col_a, col_b = st.columns(2)
    with col_a:
        cari_nama = st.text_input("Nama Mahasiswa:")
    with col_b:
        input_hadir = st.number_input("Jumlah Hadir (Opsional):", min_value=0, value=0, step=1)

    if st.button("Proses Data"):
        if cari_nama:
            # 1. Cari data di database
            hasil = df[df["Nama"].str.contains(cari_nama, case=False, na=False)]
            
            if not hasil.empty:
                data_asli = hasil.iloc[0]
                
                # Tampilkan Tabel Data Mahasiswa yang ditemukan
                st.write(f"Ditemukan data untuk: **{data_asli['Nama']}**")
                cols_show = ["Nama", "Hadir", "Persentase_Hadir", "Kategori"]
                st.dataframe(hasil[cols_show], use_container_width=True)
                
                # 2. Logika Verifikasi (Jika ada input hadir)
                if input_hadir > 0:
                    hadir_asli = data_asli["Hadir"]
                    if int(input_hadir) == int(hadir_asli):
                        st.success(f"✅ **Verifikasi Berhasil**: Data sinkron! {data_asli['Nama']} masuk kategori **{data_asli['Kategori']}**.")
                    else:
                        st.error(f"⚠️ **Verifikasi Gagal**: Data kehadiran yang Anda masukkan ({input_hadir}x) tidak cocok dengan catatan sistem kami ({hadir_asli}x).")
                else:
                    # Jika tidak ada input hadir, cukup tampilkan kategori
                    st.info(f"Mahasiswa **{data_asli['Nama']}** saat ini berada di kategori **{data_asli['Kategori']}**")
            else:
                st.warning("Nama mahasiswa tidak ditemukan.")
        else:
            st.error("Silakan masukkan nama mahasiswa terlebih dahulu.")

   # =========================================================
    # BAGIAN: FEEDBACK MAHASISWA & REKAP STATISTIK
    # =========================================================
    st.divider()
    st.subheader("📝 Feedback Penggunaan Web")
    
    # --- MENAMPILKAN ANGKA STATISTIK ---
    # Baca buku catatan kita
    df_baca_fb = pd.read_csv(FILE_FEEDBACK)
    
    # Hitung jumlah orang untuk masing-masing pilihan
    jml_puas = len(df_baca_fb[df_baca_fb["Feedback"] == "Puas"])
    jml_kurang = len(df_baca_fb[df_baca_fb["Feedback"] == "Kurang Puas"])
    jml_gangguan = len(df_baca_fb[df_baca_fb["Feedback"] == "Banyak Gangguan"])
    
    # Tampilkan dalam satu kotak kecil menggunakan st.info
    st.info(f"📊 **Statistik Saat Ini:** 👍 Puas: **{jml_puas}** |  😢 Kurang Puas: **{jml_kurang}** |  😡 Banyak Gangguan: **{jml_gangguan}**")
    
    st.write("---")
    st.write("Bagaimana pengalaman kamu mengakses web ini hari ini?")

    # --- FUNGSI EFEK NGEPOP ---
    def efek_ngepop_css(emoji):
        html_code = f"""
        <style>
        @keyframes popUp {{
            0% {{ transform: scale(0.5) translateY(0px); opacity: 1; }}
            50% {{ transform: scale(1.5) translateY(-60px); opacity: 1; }}
            100% {{ transform: scale(1) translateY(-120px); opacity: 0; }}
        }}
        .emoji-container {{
            position: fixed;
            bottom: 50px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            font-size: 60px;
            display: flex;
            gap: 20px;
            pointer-events: none;
        }}
        .emoji-pop {{
            animation: popUp 1.5s ease-out forwards;
        }}
        .emoji-pop:nth-child(1) {{ animation-delay: 0s; }}
        .emoji-pop:nth-child(2) {{ animation-delay: 0.15s; }}
        .emoji-pop:nth-child(3) {{ animation-delay: 0.3s; }}
        </style>
        <div class="emoji-container">
            <div class="emoji-pop">{emoji}</div>
            <div class="emoji-pop">{emoji}</div>
            <div class="emoji-pop">{emoji}</div>
        </div>
        """
        st.markdown(html_code, unsafe_allow_html=True)

    # --- TOMBOL FEEDBACK ---
    col_fb1, col_fb2, col_fb3 = st.columns(3)

    with col_fb1:
        if st.button("Puas 👍", use_container_width=True):
            simpan_feedback(st.session_state.nim, "Puas") # Simpan ke catatan
            st.success("Terima kasih! Senang web ini bisa berjalan lancar untukmu.")
            efek_ngepop_css("👍") # Munculkan animasi
            
    with col_fb2:
        if st.button("Kurang Puas 😢", use_container_width=True):
            simpan_feedback(st.session_state.nim, "Kurang Puas") # Simpan ke catatan
            st.warning("Terima kasih atas feedback-nya. Kami akan terus meningkatkannya!")
            efek_ngepop_css("😢") # Munculkan animasi

    with col_fb3:
        if st.button("Banyak Gangguan 😡", use_container_width=True):
            simpan_feedback(st.session_state.nim, "Banyak Gangguan") # Simpan ke catatan
            st.error("Mohon maaf atas ketidaknyamanannya. Tim kami akan mengecek kendala ini.")
            efek_ngepop_css("😡") # Munculkan animasi

    st.divider()

    # =========================================================
    # BAGIAN: LOGOUT
    # =========================================================
    st.divider()
    
    col1, col2, col3 = st.columns([3, 2, 3])

    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.login = False
            st.rerun()