from flask import Flask, jsonify
from flask import request
import firebase_admin
from firebase_admin import credentials, firestore,storage
from email.encoders import encode_base64
import os
import sys
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
# from email.header import Header
import os
from email.mime.base import MIMEBase
from email import encoders
import logging
from datetime import datetime
import urllib3
import tempfile
import mimetypes
#--------for sendgrid--------------
from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment
from sendgrid.helpers.mail import (Mail,Email,To,Content, Attachment, FileContent, FileName, FileType, Disposition,Header)
import base64
# Load the environment variables
from dotenv import load_dotenv
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
#--------for sendgrid--------------
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# import win32com.client as client
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.DEBUG)
logging.basicConfig()

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
        
    # this function will send mail and save data in firebase database
    def send_mail(self, data, files=None):
        # Create a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response = None 
        try:
            notification_mail_ref = self.db.collection('notification_mail_mst')
            user_mail_ref = self.db.collection('user_mst_2')
            receiver_email = []

            # Ensure user_property is treated as a number (it might come as a string from the frontend)
            user_property = int(data["user_property"]) if data["user_property"] else None
            if user_property is not None:
                # Query the user_mail_ref collection using the user_property
                receiver = user_mail_ref.where('user_property', '==', user_property).get()

                # Debugging: Print the number of documents returned
                print(f"Found {len(receiver)} receivers for user_property: {user_property}")

                # Iterate over the documents in the query result
                for val in receiver:
                    email = val.get('user_email')
                    if email:
                        receiver_email.append(email)

            # Ensure necessary data is present
            if not all(key in data for key in ['mailSubject', 'mailBody']):
                raise ValueError("Missing required email information")

            # Ensure there are recipients
            if not receiver_email:
                raise ValueError("No recipients found for the specified user property")
            # -----------------it is for email server-----------------
            # # Email server settings
            # SERVER = "mail.xorgeek.com"
            # PORT = 587  # Port for TLS
            # FROM = "nazad@xorgeek.com"
            # cc_email_list = data.get('cc', [])
            # PASSWORD = "@#$ASFJ@#$" 

            # # Combine "To" and "CC" email lists for sending
            # all_recipients = receiver_email + cc_email_list
            # -----------------it is for email server-----------------
            
            SUBJECT = data["mailSubject"]
            TEXT = data["mailBody"]
            # -----------------it is for Sendgrid server-----------------
            # SendGrid API Key
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            # Encode the subject to UTF-8 (for Japanese or other non-ASCII text)
            encoded_subject = SUBJECT.encode('utf-8').decode('utf-8')
            print('SS------------------',encoded_subject)
            encoded_content = TEXT.encode('utf-8')
            # -----------------it is for Sendgrid server-----------------

            # -----------------it is for Email server-----------------
            # # Prepare the email headers and message
            # msg = MIMEMultipart()
            # msg['From'] = FROM
            # msg['To'] = ', '.join(receiver_email)
            # msg['Subject'] = Header(SUBJECT, 'utf-8')
            # msg['Reply-To'] = "no-reply@xorgeek.com"
            # if cc_email_list:
            #     msg['Cc'] = ', '.join(cc_email_list)
            
            # body = MIMEText(TEXT, 'plain', 'utf-8')
            # msg.attach(body)
            # -----------------it is for Email server-----------------
            # -----------------it is for Sendgrid server-----------------
            # Prepare the email headers and message
            from_email = Email("sohel@xorgeek.com")
            to_emails = [To(email) for email in receiver_email]
            subject = encoded_subject  # Use the encoded subject
            content = Content("text/plain", encoded_content.decode('utf-8'))  # Decode for SendGrid
            print('content-----------------',content)
            # Create the Mail object
            mail = Mail(from_email, to_emails, subject, content)
            mail.reply_to = Email("sohel@xorgeek.com")
            print("Payload being sent to SendGrid:", mail.get())
            # -----------------it is for Sendgrid server-----------------

            file_names = [None] * 5
            file_urls = [None] * 5  # To store the URLs of the uploaded files

            # Process file attachments if provided
            if files:
                bucket = storage.bucket()  # Get the Firestore Storage bucket
                for index, file in enumerate(files):
                    if index >= 5:
                        break
                    if file and hasattr(file, 'filename'):
                        # Create a unique filename with the timestamp in the 'notification' folder
                        file_name = f"notificationMail/{timestamp}_{file.filename}"  # Prefix the filename with the timestamp
                        blob = bucket.blob(file_name)

                        file.seek(0)  # Reset file pointer before uploading
                        # Upload the file to Firestore Storage
                        blob.upload_from_string(file.read(), content_type=file.content_type)

                        # Make the file publicly accessible (optional)
                        blob.make_public()
                        # Get the file URL
                        file_urls[index] = blob.public_url
                        file.seek(0)  # Reset file pointer before attaching to email
                        
                        # -----------------it is for Email server-----------------
                        
            #             # Attach the file to the email
            #             part = MIMEBase("application", "octet-stream")
            #             part.set_payload(file.read())
            #             encoders.encode_base64(part)
            #             part.add_header("Content-Disposition", f"attachment; filename={file.filename}")
            #             msg.attach(part)
            #             file_names[index] = file.filename

            # # Connect to the server
            # server = smtplib.SMTP(SERVER, PORT)
            # server.set_debuglevel(1)
            # server.starttls()  # Upgrade the connection to TLS

            # # Login to the server
            # server.login(FROM, PASSWORD)

            # # Send the email
            # for receiver_mail in receiver_email:
            #     server.sendmail(FROM, receiver_mail, msg.as_string())
            # server.quit()
            # -----------------it is for Email server-----------------
            # -----------------it is for Sendgrid server--------------
                        # Attach the file to the email
                        encoded_content = base64.b64encode(file.read()).decode('utf-8')  # Encode content
                        mime_type, _ = mimetypes.guess_type(file.filename)  # Determine MIME type
                        attachedFile = Attachment(
                                            FileContent(encoded_content),
                                            FileName(file.filename),
                                            FileType( mime_type or "application/octet-stream"),
                                            Disposition('attachment')
                                        )
                        
                        mail.add_attachment(attachedFile)
                        file_names[index] = file.filename
                        

            # Send the email via SendGrid API
            try:
                #print('message is sending--------Pay Load--------',mail.get())
                response = sg.send(mail)
            except Exception as e:
                print(f"Error sending email: {e}")
                if hasattr(e, 'status_code'):
                    print(f"Status Code: {e.status_code}")
                if hasattr(e, 'body'):
                    print(f"Error Body: {e.body}")
            # -----------------it is for Sendgrid server--------------

            # Check the response
            if response.status_code == 202:
                logger.info("Email sent successfully!")

            # Create custom document ID 
            doc_id = f"{user_property}_{timestamp}"

            # Save notification data to the database
            now = datetime.now()
            Date = now.strftime("%Y/%m/%d %H:%M:%S")
            # Save file names in Firestore, using None for fields that have no associated file
            notification_data = {
                'notification_mail_title': SUBJECT,
                'notification_mail_body': TEXT,
                'notification_mail_type': user_property,  # Use the updated user_property value
                'regist_date': Date,
                'notification_mail_file_name_1': f"{timestamp}_{file_names[0]}" if file_names[0] else None,
                'notification_mail_file_name_2': f"{timestamp}_{file_names[1]}" if file_names[1] else None,
                'notification_mail_file_name_3': f"{timestamp}_{file_names[2]}" if file_names[2] else None,
                'notification_mail_file_name_4': f"{timestamp}_{file_names[3]}" if file_names[3] else None,
                'notification_mail_file_name_5': f"{timestamp}_{file_names[4]}" if file_names[4] else None,
            }

            # Add data to Firestore with custom document ID
            notification_mail_ref.document(doc_id).set(notification_data)
            logger.info("Email sent successfully!")

            return {'status': 'success', 'message': 'Email sent successfully'}, 200

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {'status': 'error', 'message': str(e)}, 500

        # ---------------------------------update_notificationmail---------------------------------------------------
        
    def update_notificationmail(self, uid, data):
        try:
            # Firebase Firestore and Storage setup
            notification_mail_ref = self.db.collection('notification_mail_mst')
            bucket = storage.bucket()  # Firebase storage bucket
            
            # Email details
            receiver_email = []
            user_mail_ref = self.db.collection('user_mst_2')

            # Debug: Log the user_property and data being searched
            print(f"Searching for users with user_property: {data['notification_mail_type']}")
            
            # Query Firestore to get users based on notification_mail_type
            receiver = user_mail_ref.where('user_property', '==', int(data["notification_mail_type"])).get()
            print([doc.id for doc in receiver])
            
            # Check if we got any recipients
            if not receiver:
                raise ValueError("No recipients found for the specified user property")
            else:
                print(f"Found {len(receiver)} recipients")

            # Collect all the emails from the query results
            for val in receiver:
                email = val.get('user_email')
                if email:
                    receiver_email.append(email)
            
            # Ensure necessary data for the email
            if not all(key in data for key in ['notification_mail_title', 'notification_mail_body']):
                raise ValueError("Missing required email information")

            if not receiver_email:
                raise ValueError("No recipients found for the specified user property")
            
            # -----------------it is for email server-----------------
            # # Email preparation
            # msg = MIMEMultipart()
            # msg['From'] = "nazad@xorgeek.com"
            # msg['To'] = ', '.join(receiver_email)
            # msg['Subject'] = Header(data["notification_mail_title"], 'utf-8')
            # msg['Reply-To'] = "no-reply@xorgeek.com"
            # msg.attach(MIMEText(data["notification_mail_body"], 'plain', 'utf-8'))
            # -----------------it is for email server-----------------
            # -----------------it is for Sendgrid server-----------------
            SUBJECT = data["notification_mail_title"]
            TEXT = data["notification_mail_body"]
            # SendGrid API Key
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            # Encode the subject to UTF-8 (for Japanese or other non-ASCII text)
            encoded_subject = SUBJECT.encode('utf-8').decode('utf-8')
            print('SS------------------',encoded_subject)
            encoded_content = TEXT.encode('utf-8')
            # Prepare the email headers and message
            from_email = Email("sohel@xorgeek.com")
            to_emails = [To(email) for email in receiver_email]
            subject = encoded_subject  # Use the encoded subject
            content = Content("text/plain", encoded_content.decode('utf-8'))  # Decode for SendGrid
            print('content-----------------',content)
            # Create the Mail object
            mail = Mail(from_email, to_emails, subject, content)
            mail.reply_to = Email("sohel@xorgeek.com")
            print("Payload being sent to SendGrid:", mail.get())
            # -----------------it is for Sendgrid server-----------------

            # Retrieve file names
            file_names = [
                data.get('notification_mail_file_name_1'),
                data.get('notification_mail_file_name_2'),
                data.get('notification_mail_file_name_3'),
                data.get('notification_mail_file_name_4'),
                data.get('notification_mail_file_name_5')
            ]

            # Flag to check if any files are attached
            files_attached = False

            # Retrieve files from Firebase Storage and attach them to the email
            for file_name in file_names:
                if file_name and file_name.strip():
                    print(f"Processing file: {file_name}")
                    blob = bucket.blob(f"notificationMail/{file_name}")

                    if not blob.exists():
                        print(f"Blob {file_name} does not exist.")
                        continue  # Skip to the next file name if it doesn't exist

                    try:
                        # Use a temporary file to download
                        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                            blob.download_to_file(temp_file)  # Download file to temp
                            temp_file.seek(0)  # Go back to the start of the file
                            #file_data = temp_file.read()  # Read the file data

                        # # Attach file to the email
                        # part = MIMEBase('application', 'octet-stream')
                        # part.set_payload(file_data)
                        # encoders.encode_base64(part)
                        # part.add_header("Content-Disposition", f"attachment; filename={file_name}")
                        # msg.attach(part)  # Attach the part to the email message
                        # files_attached = True  # Mark that we have at least one file attached
                        # -----------------it is for Sendgrid server--------------
                        # Attach the file to the email
                        encoded_content = base64.b64encode(temp_file.read()).decode('utf-8')  # Encode content
                        mime_type, _ = mimetypes.guess_type(temp_file.filename)  # Determine MIME type
                        attachedFile = Attachment(
                                            FileContent(encoded_content),
                                            FileName(temp_file.filename),
                                            FileType( mime_type or "application/octet-stream"),
                                            Disposition('attachment')
                                        )
                        
                        mail.add_attachment(attachedFile)
                        
                        # -----------------it is for Sendgrid server--------------

                    except Exception as e:
                        print(f"Failed to download {file_name}: {e}")
                        continue  # Skip to the next file name if there's an error
                else:
                    print("No valid file name provided; skipping...")

            # Check if any files were attached before sending the email
            if files_attached:
                print("Sending email with attachments...")
            else:
                print("No files to attach. Email will not be sent.")
            # -----------------it is for Email server--------------
            # # Send email
            # server = smtplib.SMTP("mail.xorgeek.com", 587)
            # server.starttls()
            # server.login("nazad@xorgeek.com", "R+GI?#10=P")
            # for email in receiver_email:
            #     server.sendmail("nazad@xorgeek.com", email, msg.as_string())
            # server.quit()
            # -----------------it is for Email server--------------
            # -----------------it is for Sendgrid server--------------
            # Send the email via SendGrid API
            try:
                print('message is sending--------Pay Load--------',mail.get())
                response = sg.send(mail)
            except Exception as e:
                print(f"Error sending email: {e}")
                if hasattr(e, 'status_code'):
                    print(f"Status Code: {e.status_code}")
                if hasattr(e, 'body'):
                    print(f"Error Body: {e.body}")
            # Check the response
            if response.status_code == 202:
                logger.info("Email sent successfully!")
            # -----------------it is for Sendgrid server--------------

            # Update Firestore with the email details
            now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            updated_data = {
                'notification_mail_title': data["notification_mail_title"],
                'notification_mail_body': data["notification_mail_body"],
                'notification_mail_type': data["notification_mail_type"],
                'update_date': now,
                'notification_mail_file_name_1': file_names[0] if file_names[0] else None,
                'notification_mail_file_name_2': file_names[1] if file_names[1] else None,
                'notification_mail_file_name_3': file_names[2] if file_names[2] else None,
                'notification_mail_file_name_4': file_names[3] if file_names[3] else None,
                'notification_mail_file_name_5': file_names[4] if file_names[4] else None
            }

            # Updating Firestore document with new details
            notification_mail_ref.document(uid).set(updated_data, merge=True)

            return {'status': 'success', 'message': 'Email updated and sent successfully'}, 200

        except Exception as e:
            print(f"Error occurred: {e}")
            return {'status': 'error', 'message': str(e)}, 500



        
    def fetch_all_mail(self,query_params=None):
        try:
            # set query from notification_mail_mst
            query = self.db.collection('notification_mail_mst')
            
            # Apply filters based on query parameters
            if query_params:
                if 'notification_start_date' in query_params:
                    query = query.where('regist_date', '>=', query_params.get('notification_start_date'))

                if 'notification_end_date' in query_params:
                    query = query.where('regist_date', '<=', query_params.get('notification_end_date'))
                    
                if 'notification_mail_title' in query_params:
                    title = query_params.get('notification_mail_title')
                    query = query.where('notification_mail_title', '>=', title).where('notification_mail_title', '<', title + '\uf8ff')
                    
                if 'notification_mail_body' in query_params:
                    title = query_params.get('notification_mail_body')
                    query = query.where('notification_mail_body', '>=', title).where('notification_mail_body', '<', title + '\uf8ff')
            
            # Calculate the total number of documents before applying pagination
            all_docs = list(query.stream())
            total_count = len(all_docs)
            
            # Set pagination defaults
            page = int(query_params.get('page', 1)) if query_params else 1
            limit = int(query_params.get('limit', 10)) if query_params else 10
            offset = (page - 1) * limit

            # Apply pagination using offset and limit
            query = query.offset(offset).limit(limit)
            paginated_docs = query.stream()
            
            # Fetch the paginated documents and prepare the response
            notifications = []
            for notification_doc in paginated_docs:
                notification_data = notification_doc.to_dict()
                notification_data['document_id'] = notification_doc.id  # Add document ID
                notification_data['total_count'] = total_count  # Add total count
                notifications.append(notification_data)

            # Return the notifications and a 200 status
            return notifications, 200
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {'status': 'error', 'message': str(e)}, 500
