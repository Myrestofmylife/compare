import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Update VALINS Sistem", layout="wide")
st.title("🔄 Update Data VALINS dari CSV (Delimiter: |)")

st.markdown("""
**Langkah-langkah:**
1. Upload **Data Awal** (.xlsx atau .csv)
2. Upload **CSV Update** (delimiter `|`)
3. Klik tombol **Proses Update**
4. Download hasil update

🔎 Kolom kunci:
- `ONU SN`
- `ID VALINS`
- `TGL UPDATE SISTEM`
""")

# Upload data awal
data_awal_file = st.file_uploader("📁 Upload Data Awal (Excel/CSV)", type=["xlsx", "csv"])

# Upload data update
data_csv_file = st.file_uploader("📄 Upload CSV Update (delimiter '|')", type=["csv"])

if data_awal_file and data_csv_file:

    # Baca data awal
    if data_awal_file.name.endswith(".xlsx"):
        df_awal = pd.read_excel(data_awal_file)
    else:
        df_awal = pd.read_csv(data_awal_file)

    # Baca data update (dengan delimiter '|')
    df_csv = pd.read_csv(data_csv_file, sep='|')
    df_csv.columns = df_csv.columns.str.strip()  # Bersihkan header CSV

    st.write("📌 Kolom CSV Update:", df_csv.columns.tolist())

    if st.button("🚀 Proses Update"):
        # Normalisasi kolom di df_awal
        df_awal['ONU SN'] = df_awal['ONU SN'].astype(str).str.strip()
        df_awal['ID VALINS'] = df_awal['ID VALINS'].fillna('').astype(str).str.strip()
        if 'TGL UPDATE SISTEM' not in df_awal.columns:
            df_awal['TGL UPDATE SISTEM'] = ''

        # Normalisasi CSV
        df_csv['ONU SN'] = df_csv['ONU SN'].astype(str).str.strip()
        df_csv['VALINS ID'] = df_csv['VALINS ID'].fillna('').astype(str).str.strip()

        updated_rows = 0

        for idx, row in df_csv.iterrows():
            valins_id = row['VALINS ID']
            onu_sn = row['ONU SN']

            if not valins_id or valins_id == '0':
                continue  # Skip jika ID tidak valid

            # Temukan baris di data awal dengan ONU SN yang sama
            match_idx = df_awal[df_awal['ONU SN'] == onu_sn].index

            if len(match_idx) == 0:
                continue  # ONU SN tidak ditemukan

            for i in match_idx:
                # Hanya update jika ID VALINS di data awal masih kosong
                if not df_awal.at[i, 'ID VALINS'] or df_awal.at[i, 'ID VALINS'] == '0':
                    df_awal.at[i, 'ID VALINS'] = valins_id
                    df_awal.at[i, 'TGL UPDATE SISTEM'] = 'Done Sistem'
                    updated_rows += 1

        st.success(f"✅ Update selesai. {updated_rows} baris berhasil diperbarui.")

        # Preview hasil
        st.subheader("🔍 Preview Data Setelah Update")
        st.dataframe(df_awal.head(20))

        # Simpan hasil
        output = BytesIO()
        df_awal.to_excel(output, index=False)
        st.download_button(
            label="⬇️ Download Hasil Update",
            data=output.getvalue(),
            file_name="data_awal_updated.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
