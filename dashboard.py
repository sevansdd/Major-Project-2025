import streamlit as st
import pandas as pd
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from dotenv import load_dotenv

# === Load Environment Variables ===
load_dotenv()
SENDER_EMAIL = os.getenv("EMAIL_USER")
SENDER_PASSWORD = os.getenv("EMAIL_PASS")
RECIPIENT_EMAIL = os.getenv("EMAIL_TO")

# === Email Sender Function ===
def send_pdf_email(pdf_path):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = "🚨 Cyber Risk Report (PDF Attached)"

    body = "Hi,\n\nPlease find attached the cyber risk report generated from the dashboard.\n\nRegards,\nCyber Triage Bot"
    msg.attach(MIMEText(body, 'plain'))

    with open(pdf_path, "rb") as file:
        part = MIMEApplication(file.read(), Name=os.path.basename(pdf_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
        msg.attach(part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")
        return False

# === Risk Chart Saver ===
def save_risk_distribution_chart(df, chart_path="risk_chart.png"):
    fig, ax = plt.subplots(figsize=(6, 4))
    df['risk_score'].hist(bins=10, edgecolor='black', ax=ax)
    ax.set_title("Risk Score Distribution")
    ax.set_xlabel("Risk Score")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    fig.savefig(chart_path)
    plt.close(fig)
    return chart_path

# === PDF Generator ===
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 14)
        self.cell(0, 10, "Cyber Triage Risk Report", ln=True, align="C")

    def summary_section(self, total, suspicious, safe):
        self.set_font("Arial", '', 12)
        self.ln(10)
        self.cell(0, 10, f"Total Records: {total}", ln=True)
        self.cell(0, 10, f"Suspicious Entries: {suspicious}", ln=True)
        self.cell(0, 10, f"Safe/Other Entries: {safe}", ln=True)
        self.ln(5)

    def insert_chart(self, chart_path):
        self.image(chart_path, x=40, y=None, w=130)
        self.ln(10)

    def table_header(self):
        self.set_font("Arial", 'B', 12)
        self.cell(30, 10, "PID", 1)
        self.cell(50, 10, "Name", 1)
        self.cell(40, 10, "Risk Score", 1)
        self.cell(40, 10, "Risk", 1)
        self.ln()

    def add_row(self, pid, name, risk_score, risk):
        self.set_font("Arial", '', 11)
        self.cell(30, 10, str(pid), 1)
        self.cell(50, 10, str(name)[:25], 1)
        self.cell(40, 10, str(risk_score), 1)
        self.cell(40, 10, str(risk), 1)
        self.ln()

def generate_pdf(df, filename="cyber_alert_report.pdf"):
    total = len(df)
    suspicious = len(df[df['risk'] == 'Suspicious'])
    safe = total - suspicious
    chart_path = save_risk_distribution_chart(df)

    pdf = PDF()
    pdf.add_page()
    pdf.summary_section(total, suspicious, safe)
    pdf.insert_chart(chart_path)
    pdf.table_header()

    for _, row in df.iterrows():
        pdf.add_row(row['pid'], row['name'], row['risk_score'], row['risk'])

    pdf.output(filename)

    if os.path.exists(chart_path):
        os.remove(chart_path)

    return filename

# === Streamlit App ===
st.title("📊 Cyber Triage Dashboard")

@st.cache_data
def load_data():
    return pd.read_csv("processed_data/final_scored.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("CSV file not found.")
    st.stop()

st.subheader("📋 Full Dataset")
st.dataframe(df)

st.subheader("📈 Risk Score Distribution")
fig, ax = plt.subplots(figsize=(6, 4))
df['risk_score'].hist(bins=10, edgecolor='black', ax=ax)
ax.set_title("Risk Score Distribution")
ax.set_xlabel("Risk Score")
ax.set_ylabel("Frequency")
st.pyplot(fig)

critical_df = df[df['risk'] == 'Suspicious']
if not critical_df.empty:
    st.subheader("🚨 Suspicious Records")
    st.dataframe(critical_df)

# === Generate + Email PDF Button ===
if st.button("📄 Generate & Email PDF Report"):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cyber_alert_report_{timestamp}.pdf"
        generate_pdf(df, filename)
        st.success("✅ PDF generated successfully!")

        if send_pdf_email(filename):
            st.success("📧 Email sent successfully.")
        else:
            st.warning("⚠ PDF created but email sending failed.")

        with open(filename, "rb") as f:
            st.download_button("⬇ Download PDF", f, file_name=filename, mime="application/pdf")

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("Click the button to generate and email the report.")
