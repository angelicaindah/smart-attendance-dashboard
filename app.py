import pandas as pd
import streamlit as st
from login import login_page

# Tambahkan library untuk clustering dan visualisasi
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

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
    st.dataframe(df, use_container_width=True)

    st.divider()

    # grafik bawaan
    st.subheader("📈 Grafik Kehadiran")
    st.bar_chart(df.set_index("Nama")["Persentase_Hadir"])

    st.divider()

    # =========================================================
    # BAGIAN: K-MEANS CLUSTERING & INSIGHT (DITAMBAHKAN)
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

        # 4. Tabel Detail (Expander)
        with st.expander("🔎 Lihat Detail Daftar Mahasiswa per Cluster"):
            st.dataframe(
                df[["Nama", "Hadir", "Persentase_Hadir", "Kategori"]],
                use_container_width=True,
            )
    else:
        st.error(f"Gagal memproses K-Means. Pastikan kolom '{kolom_X}' dan '{kolom_Y}' tersedia.")

    st.divider()

    # logout
    col1, col2, col3 = st.columns([3, 2, 3])

    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.login = False
            st.rerun()