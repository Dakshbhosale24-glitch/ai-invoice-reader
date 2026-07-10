import streamlit as st
import pdfplumber
import re
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="AI Invoice Reader",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Invoice Reader")
st.write("Welcome to your first AI product!")

uploaded_file = st.file_uploader(
    "Upload your invoice (PDF)",
    type=["pdf"]
)

if uploaded_file:

    st.success(f"Uploaded: {uploaded_file.name}")

    with pdfplumber.open(uploaded_file) as pdf:

        text = ""

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n\n"

    st.subheader("Extracted Text")
    st.write(text)

    st.subheader("📋 Invoice Information")

    invoice_number = ""
    invoice_date = ""
    customer = ""
    total = ""

    invoice_match = re.search(r"Invoice #:\s*([A-Za-z0-9\-]+)", text)
    if invoice_match:
        invoice_number = invoice_match.group(1)
        st.write("📄 Invoice Number:", invoice_number)

    date_match = re.search(r"Date:\s*(\d{1,2}\s\w+\s\d{4})", text)
    if date_match:
        invoice_date = date_match.group(1)
        st.write("📅 Date:", invoice_date)

    customer_match = re.search(r"Bill To:\s*(.*?)\s*Item", text)
    if customer_match:
        customer = customer_match.group(1)
        st.write("👤 Customer:", customer)

    total_match = re.search(r"Total\s*([^\s]+)", text)
    if total_match:
        total = total_match.group(1).replace("n", "₹")
        st.write("💰 Total Amount:", total)

    invoice_data = {
        "Invoice Number": [invoice_number],
        "Date": [invoice_date],
        "Customer": [customer],
        "Total Amount": [total]
    }

    df = pd.DataFrame(invoice_data)

    st.subheader("📊 Invoice Table")

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download CSV",
        data=csv,
        file_name="invoice_data.csv",
        mime="text/csv"
    )

    buffer = BytesIO()

with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="Invoice")

excel_data = buffer.getvalue()

st.download_button(
    label="📥 Download Excel",
    data=excel_data,
    file_name="invoice_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)