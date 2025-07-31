import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Compare ONU SN", layout="wide")
st.title("📊 Perbandingan File Excel by ONU SN")

# Mapping STO ke DATEL
sto_to_datel = {
    "BLJ": "CIKUPA", "CKA": "CIKUPA", "CSK": "CIKUPA", "KRS": "CIKUPA", "SAG": "CIKUPA", "TGR": "CIKUPA", "TJO": "CIKUPA",
    "BJO": "CILEGON", "CLG": "CILEGON", "CWN": "CILEGON", "GRL": "CILEGON", "MER": "CILEGON", "PBN": "CILEGON", "PSU": "CILEGON", "SAM": "CILEGON",
    "BAY": "LEBAK", "LBU": "LEBAK", "LWD": "LEBAK", "MEN": "LEBAK", "MLP": "LEBAK", "PDG": "LEBAK", "RKS": "LEBAK", "SKE": "LEBAK",
    "BJT": "SERANG", "BRS": "SERANG", "CKD": "SERANG", "CRS": "SERANG", "KMT": "SERANG", "SEG": "SERANG"
}

# Upload dua file
uploaded_awal = st.file_uploader("📁 Upload File Excel Awal", type=["xlsx"])
uploaded_update = st.file_uploader("📁 Upload File Excel Update", type=["xlsx"])

if uploaded_awal and uploaded_update:
    df_awal = pd.read_excel(uploaded_awal)
    df_update = pd.read_excel(uploaded_update)

    # Normalisasi kolom ONU SN
    df_awal['ONU SN'] = df_awal['ONU SN'].astype(str).str.strip()
    df_update['ONU SN'] = df_update['ONU SN'].astype(str).str.strip()

    # Pastikan kolom TGL UPDATE SISTEM ada
    if 'TGL UPDATE SISTEM' not in df_awal.columns:
        df_awal['TGL UPDATE SISTEM'] = ''

    # Tambahkan kolom UPDATE SISTEM dan KET
    df_awal['UPDATE SISTEM'] = ''
    df_awal['KET'] = ''

    # Buat dict lookup dari update
    valins_map = dict(zip(df_update['ONU SN'], df_update['VALINS ID']))

    for i, row in df_awal.iterrows():
        onu_sn = row['ONU SN']
        valins_id = valins_map.get(onu_sn, 0)

        if valins_id != 0:
            df_awal.at[i, 'UPDATE SISTEM'] = 'DONE SISTEM'
            df_awal.at[i, 'KET'] = ''
        else:
            df_awal.at[i, 'UPDATE SISTEM'] = ''
            df_awal.at[i, 'KET'] = 'Belum Update Sistem'

    # Tambahkan DATEL jika tidak ada di file update
    if 'DATEL' not in df_update.columns:
        df_update['DATEL'] = df_update['STO'].map(sto_to_datel)

    # Filter saldo baru
    df_saldo_baru = df_update[df_update['VALINS ID'] == 0]

    # Ambil kolom untuk download saldo baru
    selected_cols = [
        "WITEL", "STO", "DATEL", "NODE ID", "NODE IP", "SLOT", "PORT",
        "ONU ID", "ONU SN", "NO INET DISCOVERY", "SP TARGET"
    ]

    df_saldo_baru = df_saldo_baru[selected_cols].copy()
    df_saldo_baru.rename(columns={"SP TARGET": "ODP"}, inplace=True)
    df_saldo_baru["KET"] = "Saldo Baru"

    # Gabungkan semua hasil
    df_result = pd.concat([df_awal, df_saldo_baru], ignore_index=True)

    st.success("✅ Perbandingan selesai. Silakan unduh hasilnya.")

    # Tampilkan preview
    st.dataframe(df_result, use_container_width=True)

    # Buat file Excel untuk diunduh
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_result.to_excel(writer, index=False, sheet_name="HASIL")
    excel_data = output.getvalue()

    # Tombol download
    st.download_button(
        label="⬇️ Download Hasil Excel",
        data=excel_data,
        file_name="hasil_update_sistem.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Unggah kedua file Excel untuk memulai perbandingan.")
