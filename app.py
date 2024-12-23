import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

# Fungsi untuk membaca data dari Excel
@st.cache_resource
def load_data(file_path):
    data = pd.read_excel(file_path)
    # Distribusi nilai BU dilakukan hanya sekali di sini
    data["Good"] += data["BU"] * 0.8  # 80% BU ke Good
    data["Reject"] += data["BU"] * 0.2  # 20% BU ke Reject
    data["Total"] = data["Good"] + data["Reject"]  # Hitung Total
    data["Average"] = data["Total"] / 2  # Hitung Average
    return data

# Lokasi file Excel
file_path = "DataQC.xlsx"  # Ganti dengan lokasi file Excel Anda

# Membaca data dari file Excel
df = load_data(file_path)

# Membuat salinan data untuk tampilan, hanya untuk format angka
df_display = df.copy()
df_display["Good"] = df_display["Good"].apply(lambda x: f"{round(x):,}")
df_display["Reject"] = df_display["Reject"].apply(lambda x: f"{round(x):,}")
df_display["Total"] = df_display["Total"].apply(lambda x: f"{round(x):,}")
df_display["Average"] = df_display["Average"].apply(lambda x: f"{round(x):,}")

# Judul Dashboard
st.title("Dashboard QC Barang")
st.markdown("### Analisis Data QC Tahunan")

# Sidebar untuk filter bulan
st.sidebar.header("Filter Data")
selected_month = st.sidebar.multiselect(
    "Pilih Bulan", 
    options=df["Month"].unique(), 
    default=df["Month"].unique()
)

# Filter data berdasarkan bulan yang dipilih
filtered_data = df[df["Month"].isin(selected_month)]
filtered_display = df_display[df_display["Month"].isin(selected_month)]

# Menampilkan tabel data dengan AgGrid
st.markdown("### Data QC")

# Konfigurasi grid
gb = GridOptionsBuilder.from_dataframe(filtered_display)
gb.configure_default_column(hide=True)  # Semua kolom disembunyikan secara default
gb.configure_columns(["Month"], hide=False)  # Kolom "Month" tetap terlihat
gb.configure_columns(["Good"], hide=False)
gb.configure_columns(["Reject"], hide=False)
gb.configure_columns(["BU"], hide=False)
gb.configure_columns(["Total"], hide=False)
gb.configure_selection(selection_mode="single", use_checkbox=True)
grid_options = gb.build()

# Menampilkan data di AgGrid
AgGrid(filtered_display, gridOptions=grid_options, theme="streamlit")

# Grafik Total QC per Bulan
st.markdown("### Grafik Total QC per Bulan")
fig_total = px.bar(
    filtered_data,
    x="Month",
    y="Total",
    title="Total QC per Bulan",
    color="Month",
    labels={"Total": "Total QC", "Month": "Bulan"}
)
st.plotly_chart(fig_total)

# Grafik Rata-rata QC per Bulan
st.markdown("### Grafik Rata-rata QC")
fig_average = px.line(
    filtered_data,
    x="Month",
    y="Average",
    title="Rata-rata QC per Bulan",
    markers=True,
    labels={"Average": "Rata-rata QC", "Month": "Bulan"}
)
st.plotly_chart(fig_average)

# Grafik Rata-rata Reject per Bulan
st.markdown("### Grafik Rata-rata Reject per Bulan")
filtered_data["Reject Rate"] = (filtered_data["Reject"] / filtered_data["Total"]) * 100  # Reject rate in percentage
fig_reject = px.line(
    filtered_data,
    x="Month",
    y="Reject Rate",
    title="Rata-rata Reject per Bulan (%)",
    markers=True,
    labels={"Reject Rate": "Reject Rate (%)", "Month": "Bulan"}
)
st.plotly_chart(fig_reject)
