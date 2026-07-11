import streamlit as st
import pdfplumber
import re
import pandas as pd
import matplotlib.pyplot as plt
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

    with st.expander("📄 View Extracted Text"):
        st.write(text)

    # ---------------- Invoice Details ----------------

    invoice_number = ""
    invoice_date = ""
    customer = ""
    total = ""

    invoice_match = re.search(
        r"Invoice #:\s*([A-Za-z0-9\-]+)",
        text
    )

    if invoice_match:
        invoice_number = invoice_match.group(1)

    date_match = re.search(
        r"Date:\s*(\d{1,2}\s\w+\s\d{4})",
        text
    )

    if date_match:
        invoice_date = date_match.group(1)

    customer_match = re.search(
        r"Bill To:\s*(.*?)\s*Item",
        text,
        re.DOTALL
    )

    if customer_match:
        customer = customer_match.group(1).strip()

    total_matches = re.findall(
        r"Total:\s*([0-9,]+)",
        text,
        re.IGNORECASE
    )

    if total_matches:
        total = "₹" + total_matches[-1]
    else:
        total = "Not Found"

    st.subheader("📋 Invoice Summary")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("📄 Invoice Number", invoice_number)

    with c2:
        st.metric("📅 Date", invoice_date)

    with c3:
        st.metric("👤 Customer", customer)

    with c4:
        st.metric("💰 Total Amount", total)
            # ---------------- Invoice Items ----------------

    st.subheader("📦 Invoice Items")

    items = []

    for line in text.splitlines():

        match = re.match(
            r"(.+?)\s+(\d+)\s+(\d+)\s+(\d+)$",
            line
        )

        if match:

            items.append({
                "Item": match.group(1),
                "Qty": int(match.group(2)),
                "Unit Price": int(match.group(3)),
                "Amount": int(match.group(4))
            })

    if items:

        items_df = pd.DataFrame(items)

        st.dataframe(
            items_df,
            width="stretch"
        )

        # ---------------- Invoice Analytics ----------------

        st.subheader("📈 Invoice Analytics")

        total_items = len(items_df)
        subtotal = items_df["Amount"].sum()
        average_price = items_df["Amount"].mean()
        highest_price = items_df["Amount"].max()

        a1, a2, a3, a4 = st.columns(4)

        with a1:
            st.metric("📦 Total Items", total_items)

        with a2:
            st.metric("💰 Subtotal", f"₹{subtotal:,}")

        with a3:
            st.metric("📊 Average", f"₹{average_price:,.0f}")

        with a4:
            st.metric("🏆 Highest", f"₹{highest_price:,}")

        # ---------------- Bar Chart ----------------

        st.subheader("📊 Item Amount Chart")

        chart_data = items_df.set_index("Item")

        st.bar_chart(chart_data["Amount"])

        st.subheader("🥧 Revenue Distribution")

        fig, ax = plt.subplots(figsize=(8, 8))

        ax.pie(
            items_df["Amount"],
            labels=items_df["Item"],
            autopct="%1.1f%%",
            startangle=90
        )

        ax.axis("equal")
        st.pyplot(fig)
                
                # ---------------- Search ----------------

        st.subheader("🔍 Search in Invoice")

        search = st.text_input("Type anything to search")

        if search:

            if search.lower() in text.lower():
                st.success("✅ Found in invoice")
            else:
                st.error("❌ Not Found")

        # ---------------- Invoice Summary Table ----------------

        invoice_data = {
            "Invoice Number": [invoice_number],
            "Date": [invoice_date],
            "Customer": [customer],
            "Total Amount": [total]
        }

        df = pd.DataFrame(invoice_data)

        st.subheader("📊 Invoice Summary Table")

        st.dataframe(
            df,
            width="stretch"
        )

        # ---------------- Download Buttons ----------------

        col1, col2 = st.columns(2)

        csv = df.to_csv(index=False).encode("utf-8")

        with col1:

            st.download_button(
                label="⬇ Download CSV",
                data=csv,
                file_name="invoice_data.csv",
                mime="text/csv"
            )

        buffer = BytesIO()

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(
                writer,
                index=False,
                sheet_name="Invoice"
            )

        excel_data = buffer.getvalue()

        with col2:

            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name="invoice_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.success("✅ Invoice processed successfully!")

    else:
        st.warning("⚠️ No invoice items found in this PDF.")