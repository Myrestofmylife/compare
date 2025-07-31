import streamlit as st
import pandas as pd

st.title("🔁 Update Data Berdasarkan ONU SN & VALINS ID")

# Upload file utama (data awal)
data_awal_file = st.file_uploader("📥 Upload File Data Awal (Excel)", type=["xlsx"])
# Upload file update (Excel)
data_excel_file = st.file_uploader("📤 Upload File Excel Update", type=["xlsx"])

if data_awal_file and data_excel_file:
    df_awal = pd.read_excel(data_awal_file)
    df_update = pd.read_excel(data_excel_file)

    # Bersihkan kolom
    df_awal.columns = df_awal.columns.str.strip()
    df_update.columns = df_update.columns.str.strip()

    # Standarkan kolom ONU SN
    df_awal['ONU SN'] = df_awal['ONU SN'].astype(str).str.strip().str.upper()
    df_update['ONU SN'] = df_update['ONU SN'].astype(str).str.strip().str.upper()

    # Standarkan ID VALINS
    df_update['VALINS ID'] = df_update['VALINS ID'].fillna(0).astype(str).str.strip()

    # Flagging DONE SISTEM jika ONU SN ditemukan & VALINS ID ≠ 0
    for idx, row in df_update.iterrows():
        onu_sn = row['ONU SN']
        valins_id = row['VALINS ID']
        sp_target = row.get('SP TARGET', '')
        ket = row.get('INFO', '')

        match_idx = df_awal[df_awal['ONU SN'] == onu_sn].index

        if not match_idx.empty:
            if valins_id != '0':
                df_awal.loc[match_idx, 'TGL UPDATE SISTEM'] = 'DONE SISTEM'
                if ket:
                    df_awal.loc[match_idx, 'TGL UPDATE SISTEM'] += f" - {ket}"
        else:
            if valins_id == '0':
                # Tambah data baru
                new_row = {
                    'WITEL': row.get('WITEL', ''),
                    'STO': row.get('STO', ''),
                    'DATEL': '',
                    'NODE ID': row.get('NODE ID', ''),
                    'NODE IP': row.get('NODE IP', ''),
                    'SLOT': row.get('SLOT', ''),
                    'PORT': row.get('PORT', ''),
                    'ONU ID': row.get('ONU ID', ''),
                    'ONU SN': onu_sn,
                    'NO INET DISCOVERY': row.get('NO INET DISCOVERY', ''),
                    'ODP': f"{sp_target} (saldo baru)",
                    'TGL UPDATE SISTEM': '',
                }
                df_awal = pd.concat([df_awal, pd.DataFrame([new_row])], ignore_index=True)

    # Download hasil update
    st.success("✅ Proses Update Selesai!")

    from io import BytesIO
    output = BytesIO()
    df_awal.to_excel(output, index=False)
    st.download_button(
        label="⬇️ Download Hasil Update",
        data=output.getvalue(),
        file_name="hasil_update.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
