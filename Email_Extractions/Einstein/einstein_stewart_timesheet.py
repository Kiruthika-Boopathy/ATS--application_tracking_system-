
##=======================Sukhpreet Kang=============##

from datetime import datetime
import email
import uuid
import imaplib
from email.utils import parsedate_to_datetime
import html2text
import mysql.connector
import json

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'vrdella!6',
    'database': 'ATS'
}


def get_unread_emails(imapUserEmail, imapPassword, labels):
    imap_server = "imap.gmail.com"
    imap_port = 993

    imap_conn = imaplib.IMAP4_SSL(imap_server, imap_port)

    imap_conn.login(imapUserEmail, imapPassword)

    labels = labels
    imap_conn.select(labels)

    _, message_ids = imap_conn.search(None, "(UNSEEN)")

    unread_emails = []

    for message_id in message_ids[0].split():
        try:
            _, data = imap_conn.fetch(message_id, "(RFC822)")
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)

            subject = email_message["Subject"]
            sender = email.utils.parseaddr(email_message["From"])[1]
            body1 = ""

            # Extract the "Date" header to get the receiving time
            date_received = parsedate_to_datetime(email_message["Date"])

            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body1 = part.get_payload(decode=True).decode()
                    elif part.get_content_type() == "text/html":
                        body1 = html2text.html2text(part.get_payload(decode=True).decode())
            else:
                body1 = email_message.get_payload(decode=True).decode()

            email_data = {
                "subject": subject,
                "sender": sender,
                "body": body1,
                "date_received": date_received
            }

            unread_emails.append(email_data)
        except Exception as e:
            print(f"Error processing email: {str(e)}")

            imap_conn.store(message_id, '-FLAGS', '(\Seen)')

    imap_conn.close()

    return unread_emails


class extract_and_insert():

    def insert_into_mysql(self, formatted_results):
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            cursor = conn.cursor()

            for result in formatted_results:
                candidate_name = result.get("candidate_name", " ")
                week_start = result.get("week_start", " ")
                week_end = result.get("week_end", " ")
                ot_hours = result.get("ot_hours", " ")
                total_bill_amt = result.get("total_bill_amt", " ")
                comments = result.get("comments", " ")

                cursor.execute("SELECT placement_id FROM placement_details WHERE candidate_name = %s",
                               (candidate_name,))
                placement_id = cursor.fetchone()[0]

                if placement_id:
                    result["placement_id"] = placement_id
                else:
                    print("placement_id not found in the database.")

                cursor.execute("SELECT * FROM time_sheet WHERE placement_id = %s", (placement_id,))
                existing_record = cursor.fetchone()

                if existing_record:
                    update_query = """ UPDATE time_sheet
                                       SET
                                          week_start = %s,
                                          week_end = %s,
                                          comments = %s,
                                          ot_hours = %s,
                                          total_bill_amt = %s
                                        WHERE placement_id = %s"""
                    data_to_update = (week_start, week_end, comments, ot_hours, total_bill_amt, placement_id)

                    cursor.execute(update_query, data_to_update)
                conn.commit()
            print("Data updated successfully")
        except mysql.connector.Error as error:
            print(f"Error updating data in MySQL: {error}")
        finally:
            if conn is not None and conn.is_connected():
                cursor.close()
                conn.close()

    def email_data_information(self):
        imapUserEmail = "kiruthika.b@vrdella.com"
        imapPassword = "renm kixf nlxy avbx"
        labels = "Einstein2"

        extracted_results = []

        unread_emails = get_unread_emails(imapUserEmail, imapPassword, labels)
        for email_data in unread_emails:
            email_body = email_data["body"]
            email_subject = email_data["subject"]
            lines = email_body.split("\n")
            result = {}
            comments = []
            extracted_results = []
            for line in lines:
                if line.startswith("Job ID#"):
                    time_sheet_id = line.split(":", 1)[1].strip(" ")
                    comments.append("time_sheet_id:" + time_sheet_id)
                elif line.startswith("Job Name"):
                    job_name = line.split(":", 1)[1].strip(" ")
                    comments.append("job_name:" + job_name)
                elif line.startswith("Location"):
                    location = line.split(":", 1)[1].strip(" ")
                    comments.append("location:" + location)
                elif line.startswith("Approved By"):
                    approved_by = line.split(":", 1)[1].strip(" ")
                    comments.append("approved_by:" + approved_by)
                elif line.startswith("Contractor"):
                    result["candidate_name"] = line.split(":", 1)[1].strip(" ")
                elif line.startswith("Timesheet Dates"):
                    week_start = line.split(":", 1)[1].split("-", 1)[0].strip(" ")
                    week_start_date = datetime.strptime(week_start, '%m/%d/%Y').date()
                    week_date = datetime.strftime(week_start_date, '%d/%m/%Y')
                    result["week_start"] = week_date

                    week_end = line.split("-", 1)[1].strip(" ")
                    week_end_date = datetime.strptime(week_end, '%m/%d/%Y').date()
                    week_dates = datetime.strftime(week_start_date, '%d/%m/%Y')
                    result["week_end"] = week_dates
                elif line.startswith("Regular Time Hours"):
                    regular_time_hours = line.split(":", 1)[1].strip(" ")
                    comments.append("regular_time_hours:" + regular_time_hours)
                elif line.startswith("Over Time Hours"):
                    result["ot_hours"] = line.split(":", 1)[1].strip(" ")

                elif line.startswith("Double Time Hours"):
                    double_time_hours = line.split(":", 1)[1].strip(" ")
                    comments.append("double_time_hours:" + double_time_hours)
                elif line.startswith("Regular Bill Rate"):
                    regular_bill_rate = line.split(":", 1)[1].strip(" ")
                    comments.append("regular_bill_rate:" + regular_bill_rate)
                elif line.startswith("Over Time Bill Rate"):
                    overtime_bill_rate = line.split(":", 1)[1].strip(" ")
                    comments.append("overtime_bill_rate:" + overtime_bill_rate)
                elif line.startswith("Total Bill Rate"):
                    result["total_bill_amt"] = line.split(":", 1)[1].strip(" ").strip("$")

            result["comments"] = " ".join(comments)
            if all(result.values()):
                extracted_results.append(result)

            formatted_results = []
            for result in extracted_results:
                formatted_result = {
                    "candidate_name": result.get("candidate_name", " "),
                    "week_start": result.get("week_start", " "),
                    "week_end": result.get("week_end", " "),
                    "ot_hours": result.get("ot_hours", " "),
                    "total_bill_amt": result.get("total_bill_amt", " "),
                    "comments": result.get("comments", " ")}

            formatted_results.append(formatted_result)
            self.insert_into_mysql(formatted_results)
            print(formatted_results)


my_instance = extract_and_insert()
my_instance.email_data_information()

