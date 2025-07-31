import streamlit as st
import pandas as pd
from io import BytesIO

st.title("🔄 Update ID VALINS & Flag ke Data Awal")

st.markdown("""
Upload dua file berikut:
1. **Data Awal** (Excel/CSV) → akan dijadikan basis utama.
2. **Data Update** (CSV) → sebagai referensi update.

🟢 Hanya baris dengan `VALINS ID` ≠ 0 yang diproses  
🛑 Jika `ONU SN` belum ada di data awal → tidak diupdate  
✅ Jika `ONU SN` ada & `ID VALINS` di data awal kosong → akan diupdate dan diberi flag `Done Sistem`
""")

# Upload data awal
data_awal_file = st.file_uploader("📁 Upload Data Awal (Excel/CSV)", type=["xlsx", "csv"])
# Upload data CSV update
data_csv_file = st.file_uploader("📄 Upload Data Update CSV", type=["csv"])

if data_awal_file and data_csv_file:
    # Baca file awal
    if data_awal_file.name.endswith(".xlsx"):
        df_awal = pd.read_excel(data_awal_file)
    else:
        df_awal = pd.read_csv(data_awal_file)

    # Baca CSV update
    df_csv = pd.read_csv(data_csv_file)

    if st.button("🚀 Proses Update"):
        updated_rows = 0

        # Normalisasi data
        df_awal['ONU SN'] = df_awal['ONU SN'].astype(str).str.strip()
        df_awal['ID VALINS'] = df_awal['ID VALINS'].fillna('').astype(str).str.strip()
        if 'TGL UPDATE SISTEM' not in df_awal.columns:
            df_awal['TGL UPDATE SISTEM'] = ''

        df_csv['ONU SN'] = df_csv['ONU SN'].astype(str).str.strip()
        df_csv['VALINS ID'] = df_csv['VALINS ID'].fillna('').astype(str).str.strip()

        for idx, row in df_csv.iterrows():
            valins_id = row['VALINS ID']
            onu_sn = row['ONU SN']

            if not valins_id or valins_id == '0':
                continue  # Skip jika ID tidak valid

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

        st.subheader("📄 Preview Data Awal Setelah Update")
        st.dataframe(df_awal.head(20))

        # Simpan hasil ke Excel
        output = BytesIO()
        df_awal.to_excel(output, index=False)

        st.download_button(
            label="⬇️ Download Hasil Update (Excel)",
            data=output.getvalue(),
            file_name="data_awal_updated.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
