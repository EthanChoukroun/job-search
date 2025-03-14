import os
import pandas as pd
import schedule
import time
import base64
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# OAuth Scopes for Gmail API
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# Authenticate and get Gmail API service
def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secret_343319308440-ib5pg5184ub06dg0h6i9i8ji0umt2cn0.apps.googleusercontent.com.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

# Generate email based on format
def generate_email(first_name, last_name, format_type, company_domain):
    first_name = first_name.lower()
    last_name = last_name.lower()

    if format_type == "first_last":
        return f"{first_name}.{last_name}@{company_domain}"
    elif format_type == "f_last":
        return f"{first_name[0]}{last_name}@{company_domain}"
    elif format_type == "firstl":
        return f"{first_name}{last_name[0]}@{company_domain}"
    elif format_type == 'first':
        return f"{first_name}@{company_domain}"
    elif format_type == 'test':
        return f"ethan.chkrn@gmail.com"
    elif format_type == 'test2':
        return "nabildamlouji1@gmail.com"
    else:
        raise ValueError("Unsupported email format!")

# Create an email message with an attachment
# def create_email(sender_email, recipient_email, subject, body_text, attachment_path):
#     message = MIMEMultipart()
#     message["From"] = sender_email
#     message["To"] = recipient_email
#     message["Subject"] = subject

#     # Attach email body
#     message.attach(MIMEText(body_text, "plain"))

#     # Attach file if provided
#     if attachment_path:
#         with open(attachment_path, "rb") as attachment:
#             part = MIMEBase("application", "octet-stream")
#             part.set_payload(attachment.read())
#             encoders.encode_base64(part)
#             part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(attachment_path)}"')
#             message.attach(part)

#     raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
#     return {"raw": raw_message}

def create_email(sender_email, recipient_email, subject, body_html, attachment_path):
    """Creates an HTML email with optional attachments."""
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # Attach email body as HTML
    message.attach(MIMEText(body_html, "html"))

    # Attach file if provided
    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(attachment_path)}"')
            message.attach(part)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}

# Send email using Gmail API
def send_email(service, recipient_email, subject, body_text, attachment_path):
    sender_email = "ethan.choukroun@berkeley.edu"
    email_message = create_email(sender_email, recipient_email, subject, body_text, attachment_path)

    try:
        service.users().messages().send(userId="me", body=email_message).execute()
        print(f"✅ Sent email to {recipient_email}")
    except HttpError as error:
        print(f"❌ Failed to send email to {recipient_email}: {error}")

# Schedule email for a specific date and time
def schedule_email(service, recipient_email, subject, body_text, attachment_path, schedule_datetime):
    def job():
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        if current_time == schedule_datetime:
            send_email(service, recipient_email, subject, body_text, attachment_path)
            print(f"📅 Sent scheduled email to {recipient_email} at {schedule_datetime}")
            return schedule.CancelJob  # Remove the job after execution

    # Schedule the job to run every minute and check if it's the correct time
    schedule.every().minute.do(job)
    print(f"⏳ Email to {recipient_email} scheduled for {schedule_datetime}")

# Process the contact list and send emails
def process_and_send_emails(csv_file, email_format, company_domain, subject, resume_choice, send_now=True, schedule_datetime=None):
    df = pd.read_csv(csv_file)
    service = get_gmail_service()

    for _, row in df.iterrows():
        first_name, last_name= row["first_name"], row["last_name"]
        recipient_email = generate_email(first_name, last_name, email_format, company_domain)

        # Choose Resume
        script_dir = os.path.dirname(os.path.abspath(__file__))
        resume_path_norm = os.path.join(script_dir, "../Resumes/Ethan_Choukroun_resf.pdf") if resume_choice == 1 else os.path.join(script_dir, "../Resumes/Ethan_Choukroun_resd.pdf")
        resume_path = os.path.abspath(resume_path_norm)
        # Customize email template
#         email_body = f"""\
# Hi {first_name},

# I hope you're doing well.

# [Your Message Here]

# Best regards,
# Your Name
# """
        email_body = f"""\
<html>
    <body>
        <p>Hi {first_name},</p>

        <p>I hope you're doing well.</p>

        <p>I wanted to reach out because I’m very excited about the opened <b>Data Scientist</b> role at <b>Hut 8</b>. The company’s mission at the intersection of <b>AI, cloud computing, and Bitcoin mining</b> is incredibly exciting, and I’d love the opportunity to contribute to the team.</p>

        <p>With a strong foundation in <b>data science and predictive modeling</b>, I believe my background aligns well with the role. 
        <br>During my time in Data Science at SeatGeek, I worked on optimizing <b>dynamic pricing models</b> and <b>predictive analytics</b>, applying <b>machine learning</b> techniques to improve market efficiency. Some key contributions include:</p>
        <ul>
            <li><b>Developing pricing algorithms</b> that optimized revenue and demand forecasting.</li>
            <li><b>Building real-time data pipelines</b> to enhance decision-making.</li>
            <li><b>Collaborating cross-functionally</b> to implement scalable ML models in production.</li>
        </ul>

        <p>I’m eager to take the next step in my career in a place like Hut 8, where I can learn from an exceptional team and apply my skills to meaningful challenges. I would love the chance to further discuss your work and how I can contribute to the company’s success.</p>


        <p>Would you be open to a quick chat?</p>

        <p>You will find my resume attached to this email.<br>
        Looking forward to hearing back from you!</p>

        <p>Best regards,<br>
        Ethan Choukroun</p>
    </body>
</html>
"""

        if send_now:
            send_email(service, recipient_email, subject, email_body, resume_path)
            update_contact_reached_email(first_name, last_name, recipient_email)
        else:
            schedule_email(service, recipient_email, subject, email_body, resume_path, schedule_datetime)

CONTACT_REACHED_FILE = "contacts_reached.csv"
LINKEDIN_PROFILES_FILE = "linkedin_profiles.csv"

def update_contact_reached_email(first_name, last_name, email):
    """Update or add a contact when an email is sent."""
    
    # Load existing contacts or create a new DataFrame
    if os.path.exists(CONTACT_REACHED_FILE):
        df = pd.read_csv(CONTACT_REACHED_FILE)
    else:
        df = pd.DataFrame(columns=["first_name", "last_name", "email", "linkedin", "sent_email", "sent_linkedin"])

    # Check if contact already exists
    mask = (df["first_name"].str.lower() == first_name.lower()) & (df["last_name"].str.lower() == last_name.lower())

    if mask.any():
        # Update existing contact
        df.loc[mask, "email"] = email
        df.loc[mask, "sent_email"] = True
    else:
        # Try to find LinkedIn profile from linkedin_profiles.csv
        linkedin_url = None
        if os.path.exists(LINKEDIN_PROFILES_FILE):
            linkedin_df = pd.read_csv(LINKEDIN_PROFILES_FILE)
            linkedin_entry = linkedin_df[
                (linkedin_df["first_name"].str.lower() == first_name.lower()) &
                (linkedin_df["last_name"].str.lower() == last_name.lower())
            ]
            if not linkedin_entry.empty:
                linkedin_url = linkedin_entry.iloc[0]["linkedin_url"]

        # Add new contact
        new_row = pd.DataFrame([{
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "linkedin": linkedin_url if linkedin_url else "",
            "sent_email": True,
            "sent_linkedin": False
        }])
        df = pd.concat([df, new_row], ignore_index=True)

    # Save back to CSV
    df.to_csv(CONTACT_REACHED_FILE, index=False)

# Example Usage

process_and_send_emails(
    csv_file="contacts.csv",
    email_format="test2",  # Options: "first_last", "f_last", "firstl", "first"
    company_domain="hut8.com",  # Define company domain
    subject="Interest in Data Science at Hut 8",
    resume_choice=1,  # Choose Resume 1 or 2
    send_now=True,  # False = Schedule Send
    schedule_datetime="2025-03-15 09:00"  # Format: YYYY-MM-DD HH:MM (24-hour)
)


# Keep the script running if scheduling
while True:
    schedule.run_pending()
    time.sleep(60)