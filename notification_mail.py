from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
import logging
# import win32com.client as client

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationMail:
    def __init__(self):
        # Initialize Firebase if not already initialized
        if not firebase_admin._apps:
            try:
                cred = credentials.Certificate('permission.json')
                firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase: {e}")
                raise
        self.db = firestore.client()

    @staticmethod
    def send_mail(data):
        try:
            SERVER = "mail.xorgeek.com"
            PORT = 587  # Port for TLS
            FROM = "nazad@xorgeek.com"
            TO = data["receiver_email"]  # Must be a list
            PASSWORD = "password"  # Replace with your actual password

            SUBJECT = data["subject"]
            TEXT = data["message"]

            # Prepare actual message
            message = f"From: {FROM}\r\nTo: {', '.join(TO)}\r\nSubject: {SUBJECT}\r\n\n{TEXT}"

            # Connect to the server
            server = smtplib.SMTP(SERVER, PORT)
            # server.ehlo()  # Identifies yourself to the server
            server.starttls()  # Upgrade the connection to TLS
            # server.ehlo()  # Re-identify after starting TLS

            # Login to the server
            server.login(FROM, PASSWORD)

            # Send the email
            server.sendmail(FROM, TO, message)
            server.quit()
            logger.info("Email sent successfully!")
            
            return {'status': 'success', 'message': 'Email sent successfully'}, 200

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {'status': 'error', 'message': str(e)}, 500
