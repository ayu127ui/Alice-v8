import os
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class AlertManager:
    def __init__(self):
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from = os.getenv("TWILIO_FROM")
        self.sms_to = os.getenv("ALERT_SMS_TO")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.email_to = os.getenv("ALERT_EMAIL_TO")

    def send_sms(self, text):
        if not all([self.twilio_sid, self.twilio_token, self.twilio_from, self.sms_to]):
            return False
        client = Client(self.twilio_sid, self.twilio_token)
        client.messages.create(body=text, from_=self.twilio_from, to=self.sms_to)
        return True

    def send_email(self, subject, text):
        if not all([self.smtp_server, self.smtp_user, self.smtp_pass, self.email_to]):
            return False
        msg = MIMEText(text)
        msg["Subject"] = subject
        msg["From"] = self.smtp_user
        msg["To"] = self.email_to
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as s:
            s.starttls()
            s.login(self.smtp_user, self.smtp_pass)
            s.send_message(msg)
        return True

    def send_manual_sos(self, message):
        self.send_sms(f"SOS: {message}")
        self.send_email("SOS Alert", message)

    def send_auto_alert(self, score, labels):
        text = f"Threat detected! Score={score:.2f}, Labels={','.join(labels)}"
        self.send_sms(text)
        self.send_email("Automatic Threat Alert", text)

    def send_ppe_alert(self, ppe_data):
        """
        Send alert for PPE violations
        
        Args:
            ppe_data: Dict with violation info {type, violations_count, missing_ppe, avg_compliance}
        """
        violations_count = ppe_data.get("violations_count", 0)
        missing_ppe = ppe_data.get("missing_ppe", [])
        avg_compliance = ppe_data.get("avg_compliance", 0)
        
        missing_str = ", ".join(missing_ppe[:3])  # Show top 3
        compliance_pct = int(avg_compliance * 100)
        
        sms_text = f"PPE Alert: {violations_count} workers missing {missing_str}. Compliance: {compliance_pct}%"
        email_text = f"""PPE Safety Violation Alert

Violations Detected: {violations_count}
Missing Equipment: {', '.join(missing_ppe)}
Average Compliance: {compliance_pct}%

Please ensure all workers have required safety equipment.
"""
        
        self.send_sms(sms_text)
        self.send_email("PPE Safety Violation Alert", email_text)

    def send_alert_with_screenshot(self, labels, score, image_path):
        text = f"Threat detected! Score={score:.2f}, Labels={labels}"
        self.send_sms(text)
        
        email_body = f"""Threat Alert from Specula

Threat Score: {score:.2f}
Labels: {labels}

Screenshot attached."""
        
        try:
            if not all([self.smtp_server, self.smtp_user, self.smtp_pass, self.email_to]):
                return False
            
            msg = MIMEMultipart()
            msg["Subject"] = "Threat Alert with Screenshot"
            msg["From"] = self.smtp_user
            msg["To"] = self.email_to
            msg.attach(MIMEText(email_body))
            
            if image_path and os.path.exists(image_path):
                with open(image_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(image_path)}")
                msg.attach(part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as s:
                s.starttls()
                s.login(self.smtp_user, self.smtp_pass)
                s.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending email with screenshot: {e}")
            return False
