import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Update VALINS & Saldo Baru", layout="wide")
st.title("🔄 Update Data VALINS & Tambahkan Saldo Baru")

# Upload file
data_awal_file = st.file_uploader("📁 Upload Data Awal (Excel/CSV)", type=["xlsx", "csv"])
data_csv_file = st.file_uploader("📄 Upload CSV Update (delimiter '|')", type=["csv"])

if data_awal_file and data_csv_file:
    # Baca Data Awal
    if data_awal_file.name.endswith(".xlsx"):
        df_awal = pd.read_excel(data_awal_file)
    else:
        df_awal = pd.read_csv(data_awal_file)

    # Baca CSV update
    df_csv = pd.read_csv(data_csv_file, sep='|')
    df_csv.columns = df_csv.columns.str.strip()

    # Normalisasi
    df_awal['ONU SN'] = df_awal['ONU SN'].astype(str).str.strip()
    df_awal['ID VALINS'] = df_awal['ID VALINS'].fillna('').astype(str).str.strip()
    if 'TGL UPDATE SISTEM' not in df_awal.columns:
        df_awal['TGL UPDATE SISTEM'] = ''

    df_csv['ONU SN'] = df_csv['ONU SN'].astype(str).str.strip()
    df_csv['VALINS ID'] = df_csv['VALINS ID'].fillna('').astype(str).str.strip()

    if st.button("🚀 Proses Update & Tambah Saldo Baru"):
        updated_rows = 0
        saldo_baru_rows = []

        for idx, row in df_csv.iterrows():
            valins_id = row['VALINS ID']
            onu_sn = row['ONU SN']

            if not onu_sn:
                continue

            match_idx = df_awal[df_awal['ONU SN'] == onu_sn].index

            # === CASE 1: VALINS ID ≠ 0
            if valins_id and valins_id != '0':
                if len(match_idx) > 0:
                    for i in match_idx:
                        if not df_awal.at[i, 'ID VALINS'] or df_awal.at[i, 'ID VALINS'] == '0':
                            df_awal.at[i, 'ID VALINS'] = valins_id
                            df_awal.at[i, 'TGL UPDATE SISTEM'] = 'Done Sistem'
                            updated_rows += 1

            # === CASE 2: VALINS ID == 0 → Tambahkan baris baru (Saldo Baru)
            elif valins_id == '0':
                saldo_row = {
                    'WITEL': row.get('WITEL', ''),
                    'STO': row.get('STO', ''),
                    'DATEL': row.get('DATEL', ''),
                    'NODE ID': row.get('NODE ID', ''),
                    'NODE IP': row.get('NODE IP', ''),
                    'SLOT': row.get('SLOT', ''),
                    'PORT': row.get('PORT', ''),
                    'ONU ID': row.get('ONU ID', ''),
                    'ONU SN': row.get('ONU SN', ''),
                    'NO INET DISCOVERY': row.get('NO INET DISCOVERY', ''),
                    'ID VALINS': '',
                    'ODP': row.get('SP TARGET', ''),
                    'TGL UPDATE SISTEM': 'Saldo Baru',
                }

                # Tambahkan kolom kosong agar sesuai dengan df_awal
                for col in df_awal.columns:
                    if col not in saldo_row:
                        saldo_row[col] = ''

                saldo_baru_rows.append(saldo_row)

        # Tambahkan saldo baru ke df_awal
        if saldo_baru_rows:
            df_saldo_baru = pd.DataFrame(saldo_baru_rows)[df_awal.columns]
            df_awal = pd.concat([df_awal, df_saldo_baru], ignore_index=True)

        st.success(f"✅ {updated_rows} baris diperbarui. {len(saldo_baru_rows)} baris saldo baru ditambahkan.")

        # === TAMPILKAN HASIL ===
        st.subheader("📄 Hasil Akhir Data Awal")
        st.dataframe(df_awal.tail(20))

        # === UNDUH HASIL ===
        output_awal = BytesIO()
        df_awal.to_excel(output_awal, index=False)
        st.download_button(
            label="⬇️ Download Data Hasil Update (Termasuk Saldo Baru)",
            data=output_awal.getvalue(),
            file_name="data_awal_updated.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
