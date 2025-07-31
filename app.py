import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

st.title("🔄 Update Sistem Berdasarkan File Excel")

# Mapping STO ke DATEL
sto_to_datel = {
    'BLJ': 'CIKUPA', 'CKA': 'CIKUPA', 'CSK': 'CIKUPA', 'KRS': 'CIKUPA', 'SAG': 'CIKUPA', 'TGR': 'CIKUPA', 'TJO': 'CIKUPA',
    'BJO': 'CILEGON', 'CLG': 'CILEGON', 'CWN': 'CILEGON', 'GRL': 'CILEGON', 'MER': 'CILEGON', 'PBN': 'CILEGON', 'PSU': 'CILEGON', 'SAM': 'CILEGON',
    'BAY': 'LEBAK', 'LBU': 'LEBAK', 'LWD': 'LEBAK', 'MEN': 'LEBAK', 'MLP': 'LEBAK', 'PDG': 'LEBAK', 'RKS': 'LEBAK', 'SKE': 'LEBAK',
    'BJT': 'SERANG', 'BRS': 'SERANG', 'CKD': 'SERANG', 'CRS': 'SERANG', 'KMT': 'SERANG', 'SEG': 'SERANG'
}

# Upload file Excel
uploaded_initial = st.file_uploader("📤 Upload File Excel Data Awal", type=["xlsx"])
uploaded_update = st.file_uploader("📥 Upload File Excel Update Sistem", type=["xlsx"])

if uploaded_initial and uploaded_update:
    df_awal = pd.read_excel(uploaded_initial)
    df_update = pd.read_excel(uploaded_update)

    # Pastikan kolom 'ONU SN' dan 'VALINS ID' ada
    if 'ONU SN' in df_update.columns and 'VALINS ID' in df_update.columns:

        df_awal['TGL UPDATE SISTEM'] = df_awal['TGL UPDATE SISTEM'].astype(str)
        df_awal['ONU SN'] = df_awal['ONU SN'].astype(str)
        df_update['ONU SN'] = df_update['ONU SN'].astype(str)
        df_update['VALINS ID'] = df_update['VALINS ID'].astype(str)

        today_str = datetime.today().strftime("%Y-%m-%d")
        df_awal_updated = df_awal.copy()
        existing_onu_sn = df_awal['ONU SN'].tolist()

        # Update TGL UPDATE SISTEM
        for idx, row in df_awal_updated.iterrows():
            onu_sn = row['ONU SN']
            match_row = df_update[df_update['ONU SN'] == onu_sn]
            if not match_row.empty:
                valins_id = match_row.iloc[0]['VALINS ID']
                if valins_id != '0':
                    df_awal_updated.at[idx, 'TGL UPDATE SISTEM'] = 'Done Sistem'

        # Tambah data baru jika ONU SN belum ada dan VALINS ID = 0
        new_rows = []
        for _, row in df_update.iterrows():
            onu_sn = row['ONU SN']
            valins_id = row['VALINS ID']
            sto = row.get('STO', '').strip().upper()
            datel = sto_to_datel.get(sto, '')

            if onu_sn not in existing_onu_sn and valins_id == '0':
                new_rows.append({
                    'WITEL': row.get('WITEL', ''),
                    'STO': sto,
                    'DATEL': datel,
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

        df_result = pd.concat([df_awal_updated, pd.DataFrame(new_rows)], ignore_index=True)

        st.success(f"Hasil update: {len(new_rows)} baris ditambahkan, {df_awal_updated['TGL UPDATE SISTEM'].eq('Done Sistem').sum()} baris diperbarui.")
        st.dataframe(df_result)

        # Tombol download hasil
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Hasil Update')
            output.seek(0)
            return output

        st.download_button(
            label="⬇️ Download Excel Hasil Update",
            data=to_excel(df_result),
            file_name="hasil_update_sistem.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("Kolom 'ONU SN' dan 'VALINS ID' wajib ada di file update.")
