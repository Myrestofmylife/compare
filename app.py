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

    # Bersihkan dan standarkan kolom
    df_awal.columns = df_awal.columns.str.strip()
    df_update.columns = df_update.columns.str.strip()

    df_awal['ONU SN'] = df_awal['ONU SN'].astype(str).str.strip().str.upper()
    df_update['ONU SN'] = df_update['ONU SN'].astype(str).str.strip().str.upper()
    df_update['VALINS ID'] = df_update['VALINS ID'].fillna(0).astype(str).str.strip()

    # Kosongkan kolom update sistem dulu agar netral
    df_awal['TGL UPDATE SISTEM'] = ""

    # Buat dict update berdasarkan ONU SN
    update_dict = df_update.set_index('ONU SN').to_dict('index')

    for idx, row in df_awal.iterrows():
        onu_sn = row['ONU SN']
        if onu_sn in update_dict:
            valins_id = update_dict[onu_sn]['VALINS ID']
            if valins_id != '0':
                df_awal.at[idx, 'TGL UPDATE SISTEM'] = 'DONE SISTEM'
            else:
                df_awal.at[idx, 'TGL UPDATE SISTEM'] = 'Belum Update Sistem'

    # Tambahkan baris baru jika VALINS ID = 0 dan belum ada di data awal
    new_rows = []
    existing_onu_sn = set(df_awal['ONU SN'])

    for _, row in df_update.iterrows():
        onu_sn = row['ONU SN']
        valins_id = row['VALINS ID']

        if onu_sn not in existing_onu_sn and valins_id == '0':
            new_rows.append({
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
                'ODP': f"{row.get('SP TARGET', '')} (saldo baru)",
                'TGL UPDATE SISTEM': 'Belum Update Sistem'
            })

    if new_rows:
        df_awal = pd.concat([df_awal, pd.DataFrame(new_rows)], ignore_index=True)

    st.success("✅ Proses Update Selesai!")

    from io import BytesIO
    output = BytesIO()
    df_awal.to_excel(output, index=False)
    st.download_button(
        label="⬇️ Download Hasil Update",
        data=output.getvalue(),
        file_name="hasil_update_sistem.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
