import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
    ticket_df = pd.read_
