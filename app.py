import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="🚗 Tes3 - Selisih Golongan", layout="wide")
st.title("🚗 Laporan Selisih Naik/Turun Golongan Kendaraan")

uploaded_invoice = st.file_uploader("📄 Upload File Invoice", type=["xlsx"])
uploaded_tiket = st.file_uploader("🚘 Upload File Ticket Summary", type=["xlsx"])

def format_rupiah(x):
    return f"- Rp {abs(x):,.0f}".replace(",", ".") if x < 0 else f"Rp {x:,.0f}".replace(",", ".")

def convert_df_to_excel(df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Rekap")
    buffer.seek(0)
    return buffer

if uploaded_invoice and uploaded_tiket:
    invoice_df = pd.read_excel(uploaded_invoice, header=1)
    ticket_df = pd.read_excel(uploaded_tiket, header=1)

    invoice_df.columns = invoice_df.columns.str.strip().str.upper()
    ticket_df.columns = ticket_df.columns.str.strip().str.upper()

    invoice_df['INVOICE'] = invoice_df['NOMER INVOICE'].astype(str).str.strip()
    invoice_df['HARGA'] = pd.to_numeric(invoice_df['HARGA'], errors='coerce')
    invoice_df['KEBERANGKATAN'] = invoice_df['KEBERANGKATAN'].astype(str).str.upper().str.strip()

    ticket_df['INVOICE'] = ticket_df['NOMOR INVOICE'].astype(str).str.strip()
    ticket_df['TARIF'] = pd.to_numeric(ticket_df['TARIF'], errors='coerce') * -1

    inv = invoice_df[['INVOICE', 'KEBERANGKATAN', 'HARGA']].rename(columns={'HARGA': 'nilai', 'KEBERANGKATAN': 'pelabuhan'})
    tik = ticket_df[['INVOICE', 'TARIF']].rename(columns={'TARIF': 'nilai'})
    tik['pelabuhan'] = None

    combined_df = pd.concat([inv, tik], ignore_index=True)
    combined_df['pelabuhan'] = combined_df['pelabuhan'].fillna(method='ffill')

    sumif = combined_df.groupby('INVOICE', as_index=False).agg({
        'nilai': 'sum',
        'pelabuhan': 'first'
    })

    utama = ['MERAK', 'BAKAUHENI', 'KETAPANG', 'GILIMANUK']
    sumif['pelabuhan'] = sumif['pelabuhan'].str.upper().str.strip()
    filtered = sumif[sumif['pelabuhan'].isin(utama)]

    rekap = filtered.groupby('pelabuhan')['nilai'].sum().reindex(utama, fill_value=0).reset_index()
    rekap['keterangan'] = rekap['nilai'].apply(lambda x: 'Naik Golongan' if x < 0 else ('Turun Golongan' if x > 0 else ''))
    rekap['Selisih Naik/Turun Golongan'] = rekap['nilai'].apply(format_rupiah)

    final_df = rekap[['pelabuhan', 'Selisih Naik/Turun Golongan', 'keterangan']]
    final_df.columns = ['Pelabuhan Asal', 'Selisih Naik/Turun Golongan', 'Keterangan']

    total = rekap['nilai'].sum()
    total_row = pd.DataFrame([{
        'Pelabuhan Asal': 'TOTAL',
        'Selisih Naik/Turun Golongan': format_rupiah(total),
        'Keterangan': ''
    }])

    final_df = pd.concat([final_df, total_row], ignore_index=True)

    st.subheader("📊 Rekap Tabel")
    st.dataframe(final_df, use_container_width=True)

    st.download_button(
        "⬇️ Unduh Excel",
        data=convert_df_to_excel(final_df),
        file_name="rekap_selisih_golongan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Silakan unggah file Invoice dan Ticket Summary untuk mulai.")
