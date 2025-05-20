
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="🚗 Rekap Selisih Golongan", layout="wide")

st.markdown("<h2 style='text-align: center;'>🚗 Laporan Selisih Golongan Kendaraan</h2><hr>", unsafe_allow_html=True)
st.markdown("Proyek: **tes3** — Analisis selisih tarif golongan berdasarkan nomor invoice kendaraan.")

uploaded_invoice = st.file_uploader("📄 Upload File Invoice", type=["xlsx"])
uploaded_tiket = st.file_uploader("🚘 Upload File Ticket Summary", type=["xlsx"])

def convert_df_to_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Selisih Golongan")
    buffer.seek(0)
    return buffer

if uploaded_invoice and uploaded_tiket:
    invoice_df = pd.read_excel(uploaded_invoice, header=1)
    ticket_df = pd.read_excel(uploaded_tiket, header=1)

    invoice_df.columns = invoice_df.columns.str.strip().str.upper()
    ticket_df.columns = ticket_df.columns.str.strip().str.upper()

    invoice_df = invoice_df[['NOMER INVOICE', 'HARGA', 'KEBERANGKATAN', 'TANGGAL INVOICE']]
    ticket_df = ticket_df[['NOMOR INVOICE', 'TARIF', 'ASAL', 'TANGGAL BERANGKAT']]

    invoice_df.columns = ['INVOICE', 'HARGA_INVOICE', 'PELABUHAN', 'TANGGAL_INV']
    ticket_df.columns = ['INVOICE', 'HARGA_TIKET', 'ASAL', 'TANGGAL_TIKET']

    invoice_df['TANGGAL_INV'] = pd.to_datetime(invoice_df['TANGGAL_INV'], errors='coerce')
    ticket_df['TANGGAL_TIKET'] = pd.to_datetime(ticket_df['TANGGAL_TIKET'], errors='coerce')

    min_date = invoice_df['TANGGAL_INV'].min().date()
    max_date = invoice_df['TANGGAL_INV'].max().date()
    st.markdown(f"📅 **Periode Data Invoice:** {min_date.strftime('%d %B %Y')} s/d {max_date.strftime('%d %B %Y')}")

    merged = pd.merge(invoice_df, ticket_df, on='INVOICE', how='inner')

    merged['selisih'] = merged['HARGA_INVOICE'] - merged['HARGA_TIKET']
    merged['keterangan'] = merged['selisih'].apply(lambda x: 'Naik Golongan' if x < 0 else ('Turun Golongan' if x > 0 else 'Tetap'))

    pelabuhan_utama = ['MERAK', 'BAKAUHENI', 'KETAPANG', 'GILIMANUK']
    merged['PELABUHAN'] = merged['PELABUHAN'].str.upper().str.strip()
    filtered = merged[merged['PELABUHAN'].isin(pelabuhan_utama) & (merged['selisih'] != 0)]

    rekap = filtered.groupby('PELABUHAN')['selisih'].sum().reindex(pelabuhan_utama, fill_value=0).reset_index()
    rekap['keterangan'] = rekap['selisih'].apply(lambda x: 'Naik Golongan' if x < 0 else ('Turun Golongan' if x > 0 else ''))

    total_row = pd.DataFrame([{
        'PELABUHAN': 'TOTAL',
        'selisih': rekap['selisih'].sum(),
        'keterangan': ''
    }])

    final_df = pd.concat([rekap, total_row], ignore_index=True)

    st.subheader("📊 Rekap Selisih Tarif Golongan")
    st.dataframe(final_df, use_container_width=True)

    # Export Excel
    st.download_button(
        label="⬇️ Unduh Rekap ke Excel",
        data=convert_df_to_excel(final_df),
        file_name="rekap_selisih_golongan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("✅ Data berhasil diproses dan dapat diunduh.")

else:
    st.info("Silakan unggah kedua file Excel (Invoice dan Ticket Summary).")
