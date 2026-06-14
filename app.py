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
    # BAGIAN BARU: K-MEANS CLUSTERING & VISUALISASI
    # =========================================================
    st.subheader("🤖 Visualisasi K-Means Clustering Kehadiran Mahasiswa")

    # 1. Pilih kolom fitur untuk Clustering (sesuaikan nama kolom di CSV kamu)
    # Di sini saya asumsikan nama kolomnya: 'Total_Hadir' dan 'Persentase_Hadir'
    # Jika nama kolom jumlah kehadiranmu berbeda (misal: 'Jumlah_Kehadiran'), silakan ganti teksnya.
    kolom_X = "Hadir"
    kolom_Y = "Persentase_Hadir"

    if kolom_X in df.columns and kolom_Y in df.columns:
        X = df[[kolom_X, kolom_Y]]

        # 2. Proses K-Means (Contoh: dibagi menjadi 3 Cluster)
        kmeans = KMeans(n_clusters=3, random_state=42)
        df["Cluster"] = kmeans.fit_predict(X)

        # 3. Membuat Grafik Menggunakan Matplotlib
        fig, ax = plt.subplots(figsize=(10, 5))

        # Menggambar scatter plot dengan warna (c) berdasarkan cluster yang terbentuk
        scatter = ax.scatter(
            df[kolom_X],
            df[kolom_Y],
            c=df["Cluster"],
            cmap="viridis",
            s=100,
            edgecolors="k",
        )

        # Menambahkan label dan judul pada grafik Matplotlib
        ax.set_title(
            "Visualisasi K-Means Clustering Kehadiran Mahasiswa", fontsize=14
        )
        ax.set_xlabel("Jumlah Kehadiran", fontsize=12)
        ax.set_ylabel("Persentase Kehadiran (%)", fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.6)

        # Menampilkan legend warna cluster
        legend = ax.legend(
            *scatter.legend_elements(), title="Cluster", loc="lower right"
        )
        ax.add_artist(legend)

        # 4. Tampilkan grafik Matplotlib ke Streamlit
        st.pyplot(fig)

        # Tambahan: Menampilkan penjelasan cluster dalam bentuk dataframe (opsional)
        with st.expander("Lihat Hasil Pembagian Cluster per Mahasiswa"):
            st.dataframe(
                df[["Nama", kolom_X, kolom_Y, "Cluster"]],
                use_container_width=True,
            )
    else:
        st.error(
            f"Gagal memproses K-Means. Pastikan kolom '{kolom_X}' dan '{kolom_Y}' ada di file CSV kamu."
        )

    st.divider()

    # logout
    col1, col2, col3 = st.columns([3, 2, 3])

    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.login = False
            st.rerun()