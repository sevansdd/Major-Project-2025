import smtplib
from email.mime.text import MIMEText
import pandas as pd

def send_email_alert(subject, message, recipient_email):
    sender_email = "www.rohanpacharya318@gmail.com"
    sender_password = "pofv aoeu ujxw yoqy"  # Use Gmail App Password

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"✅ Email sent to {recipient_email} successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")

def main():
    try:
        df = pd.read_csv("processed_data/final_scored.csv")
    except Exception as e:
        print(f"❌ Failed to load CSV: {str(e)}")
        return

    if not {'pid', 'name', 'risk_score', 'risk'}.issubset(df.columns):
        print("❌ Required columns not found in CSV.")
        return

    critical = df[df['risk'] == 'Suspicious']

    if not critical.empty:
        message = "\n".join(
            [f"[FPID: {row['pid']}] Name: {row['name']} Risk Score: {row['risk_score']}" for _, row in critical.iterrows()]
        )
        print("📧 Email content:\n", message)
        send_email_alert("🚨 Cyber Triage Alert", message, "khushigurumurthy5@gmail.com")
    else:
        print("✅ No suspicious entries found.")

if __name__ == "__main__":
    main()
