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
                time_sheet_id = result.get("time_sheet_id", " ")
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
                                          time_sheet_id = %s
                                        WHERE placement_id = %s"""
                    data_to_update = (week_start, week_end, comments, time_sheet_id, placement_id)

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
        labels = "field_glass"

        extracted_results = []

        unread_emails = get_unread_emails(imapUserEmail, imapPassword, labels)
        for email_data in unread_emails:
            email_body = email_data["body"]
            email_subject = email_data["subject"]

            extracted_results = []
            result = {}
            comments = []
            if "### Time Sheet ID" in email_body:
                result["time_sheet_id"] = \
                email_body.split("### Time Sheet ID", 1)[1].split("### Time Sheet Start Date", 1)[0].replace("\n",
                                                                                                             '').replace(
                    " ", '')

            if "### Time Sheet Start Date" in email_body:
                result["week_start"] = \
                email_body.split('### Time Sheet Start Date', 1)[1].split('### Time Sheet End Date', 1)[0].replace("\n",
                                                                                                                   '').replace(
                    " ", '')

            if "### Time Sheet End Date" in email_body:
                result["week_end"] = email_body.split('### Time Sheet End Date', 1)[1].split('### Main Document ID', 1)[
                    0].replace("\n", '').replace(" ", '')

            if '### Main Document ID' in email_body:
                main_document = email_body.split("### Main Document ID", 1)[1].split("### Branch", 1)[0].replace("\n",
                                                                                                                 '').replace(
                    " ", '')
                comments.append("main_document:" + main_document)

            if '### Branch' in email_body:
                branch = email_body.split("### Branch", 1)[1].split("### Worker ID", 1)[0].replace("\n", '').replace(
                    " ", '')
                comments.append("branch:" + branch)

            if '### Worker ID' in email_body:
                worker_id = email_body.split("### Worker ID", 1)[1].split("### Worker Name", 1)[0].replace("\n",
                                                                                                           '').replace(
                    " ", '')
                comments.append("worker_id:" + worker_id)

            if '### Worker Name' in email_body:
                result["candidate_name"] = email_body.split("### Worker Name", 1)[1].split("### Work Order ID", 1)[
                    0].replace("\n", '').replace(" ", '')

            if '### Work Order ID' in email_body:
                worker_order_id = email_body.split("### Work Order ID", 1)[1].split("### Time Sheet Billable Days", 1)[
                    0].replace("\n", '').replace(" ", '')
                comments.append("worker_order_id:" + worker_order_id)

            if '### Time Sheet Billable Days' in email_body:
                time_sheet_billable_days = \
                email_body.split("### Time Sheet Billable Days", 1)[1].split("### Time Sheet Billable Hours", 1)[
                    0].replace("\n", '').replace(" ", '')
                comments.append("time_sheet_billable_days:" + time_sheet_billable_days)

            if '### Time Sheet Billable Hours' in email_body:
                time_sheet_billable_hours = \
                email_body.split('### Time Sheet Billable Hours', 1)[1].split('### Time Sheet Total Quantity', 1)[
                    0].replace("\n", '').replace(" ", '')
                comments.append("time_sheet_billable_hours: " + time_sheet_billable_hours)

            if '### Time Sheet Total Quantity' in email_body:
                time_sheet_total_quantity = email_body.split('### Time Sheet Total Quantity', 1)[1].split("---", 1)[
                    0].replace("\n", '').replace(" ", '')
                comments.append('time_sheet_total_quantity: ' + time_sheet_total_quantity)

            result["comments"] = " ".join(comments)

            if all(result.values()):
                extracted_results.append(result)

            formatted_results = []
            for result in extracted_results:
                formatted_result = {
                    "candidate_name": result.get("candidate_name", " "),
                    "time_sheet_id": result.get("time_sheet_id", " "),
                    "week_start": result.get("week_start", " "),
                    "week_end": result.get("week_end", " "),
                    "comments": result.get("comments", " ")
                }
            formatted_results.append(formatted_result)

            self.insert_into_mysql(formatted_results)

        return formatted_results


my_instance = extract_and_insert()
my_instance.email_data_information()

