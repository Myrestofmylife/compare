import streamlit as st
import pandas as pd

st.title("🔁 Update Data Berdasarkan File Excel")

# Mapping STO ke DATEL
sto_to_datel = {
    'BLJ': 'CIKUPA', 'CKA': 'CIKUPA', 'CSK': 'CIKUPA', 'KRS': 'CIKUPA',
    'SAG': 'CIKUPA', 'TGR': 'CIKUPA', 'TJO': 'CIKUPA', 'BJO': 'CILEGON',
    'CLG': 'CILEGON', 'CWN': 'CILEGON', 'GRL': 'CILEGON', 'MER': 'CILEGON',
    'PBN': 'CILEGON', 'PSU': 'CILEGON', 'SAM': 'CILEGON', 'BAY': 'LEBAK',
    'LBU': 'LEBAK', 'LWD': 'LEBAK', 'MEN': 'LEBAK', 'MLP': 'LEBAK',
    'PDG': 'LEBAK', 'RKS': 'LEBAK', 'SKE': 'LEBAK', 'BJT': 'SERANG',
    'BRS': 'SERANG', 'CKD': 'SERANG', 'CRS': 'SERANG', 'KMT': 'SERANG',
    'SEG': 'SERANG'
}

# Upload file awal
file_awal = st.file_uploader("📥 Upload File Data Awal (Excel)", type=['xlsx'])
# Upload file pembaruan
file_update = st.file_uploader("📥 Upload File Update dari Valins (Excel)", type=['xlsx'])

if file_awal and file_update:
    df_awal = pd.read_excel(file_awal)
    df_update = pd.read_excel(file_update)

    # Normalisasi kolom
    df_awal.columns = df_awal.columns.str.strip()
    df_update.columns = df_update.columns.str.strip()

    # Pastikan kolom penting ada
    for col in ['ONU SN', 'VALINS ID']:
        if col not in df_update.columns:
            st.error(f"Kolom '{col}' tidak ditemukan di file update.")
            st.stop()
    for col in ['ONU SN', 'TGL UPDATE SISTEM']:
        if col not in df_awal.columns:
            df_awal[col] = ''

    # Strip dan pastikan string
    df_awal['ONU SN'] = df_awal['ONU SN'].astype(str).str.strip()
    df_update['ONU SN'] = df_update['ONU SN'].astype(str).str.strip()
    df_update['VALINS ID'] = df_update['VALINS ID'].fillna(0).astype(str).str.strip()

    # Tambah kolom DATEL ke file update (berdasarkan STO)
    if 'STO' in df_update.columns:
        df_update['DATEL'] = df_update['STO'].map(sto_to_datel).fillna('-')
    else:
        st.warning("Kolom STO tidak ditemukan di file update. DATEL tidak ditambahkan.")

    # Proses update
    updated_rows = []
    for i, row in df_update.iterrows():
        onu_sn = row['ONU SN']
        valins_id = row['VALINS ID']

        match_index = df_awal[df_awal['ONU SN'] == onu_sn].index

        if valins_id != '0':
            if not match_index.empty:
                # ONU SN sudah ada dan VALINS ID bukan 0 -> Done Sistem
                df_awal.loc[match_index, 'TGL UPDATE SISTEM'] = 'Done Sistem'
            else:
                # ONU SN belum ada dan VALINS ID bukan 0 -> tidak diapa2in
                pass
        else:
            # VALINS ID == 0
            if not match_index.empty:
                # ONU SN sudah ada tapi VALINS ID 0 -> Belum Update Sistem
                df_awal.loc[match_index, 'TGL UPDATE SISTEM'] = 'Belum Update Sistem'
            else:
                # Data baru -> disiapkan untuk ditambahkan
                new_row = {
                    'WITEL': row.get('WITEL', ''),
                    'STO': row.get('STO', ''),
                    'DATEL': sto_to_datel.get(row.get('STO', ''), ''),
                    'NODE ID': row.get('NODE ID', ''),
                    'NODE IP': row.get('NODE IP', ''),
                    'SLOT': row.get('SLOT', ''),
                    'PORT': row.get('PORT', ''),
                    'ONU ID': row.get('ONU ID', ''),
                    'ONU SN': onu_sn,
                    'NO INET DISCOVERY': row.get('NO INET DISCOVERY', ''),
                    'ODP': row.get('SP TARGET', ''),
                    'TGL UPDATE SISTEM': 'Saldo Baru'
                }
                updated_rows.append(new_row)

    # Gabungkan data awal dengan data baru (VALINS ID = 0 dan tidak ditemukan)
    if updated_rows:
        df_new = pd.DataFrame(updated_rows)
        df_result = pd.concat([df_awal, df_new], ignore_index=True)
    else:
        df_result = df_awal.copy()

    st.success("✅ Proses update selesai!")

    # Tampilkan hasil
    st.subheader("📄 Hasil Update")
    st.dataframe(df_result)

    # Download hasil
    download_excel = df_result.to_excel(index=False, engine='openpyxl')
    st.download_button(
        label="⬇️ Download Hasil Excel",
        data=download_excel,
        file_name="hasil_update.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
