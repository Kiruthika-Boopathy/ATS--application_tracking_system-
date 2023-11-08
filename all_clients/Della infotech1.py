import datetime
# from dateutil import parser
# import re
import uuid
import email
import imaplib
from email.utils import parsedate_to_datetime
import html2text
import mysql.connector

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'vrdella!6',
    'database': 'email_extraction'
}


def get_unread_emails(email_address, password, label):
    imap_server = "imap.gmail.com"
    imap_port = 993

    imap_conn = imaplib.IMAP4_SSL(imap_server, imap_port)

    imap_conn.login(email_address, password)

    labels = label
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


class client_mail_extraction():

    def insert_data_into_mysql(self, result_data):
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            cursor = conn.cursor()

            for result_data_item in result_data:
                cursor.execute(
                    "SELECT COUNT(*) FROM client_data WHERE client_job_id = %s",
                    (result_data_item['client_job_id'],)
                )
                record_count = cursor.fetchone()[0]

                if record_count == 0:
                    update_query = """
                    INSERT INTO client_data(
                        job_title,
                        client_job_id,
                        location,
                        client,
                        client_id,
                        job_start_date,
                        job_end_date,
                        job_description,
                        job_bill_rate,
                        job_id
                    ) VALUES (
                        %(job_title)s,
                        %(client_job_id)s,
                        %(location)s,
                        %(client)s,
                        %(client_id)s,
                        %(job_start_date)s,
                        %(job_end_date)s,
                        %(job_description)s,
                        %(job_bill_rate)s,
                        %(job_id)s

                    )
                    """


                data_to_insert = {
                    "job_title": result_data_item['job_title'],
                    "client_job_id": result_data_item['client_job_id'],
                    "location": result_data_item['location'],
                    "client": result_data_item['client'],
                    "client_id": result_data_item['client_id'],
                    "job_start_date": result_data_item['job_start_date'],
                    "job_end_date": result_data_item['job_end_date'],
                    "job_description": result_data_item['job_description'],
                    "job_bill_rate": result_data_item['job_bill_rate'],
                    "job_id": str(uuid.uuid4())
                }

                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                cursor.execute(update_query, data_to_insert)

            conn.commit()
            return "Data inserted/updated successfully"
        except mysql.connector.Error as error:
            print(f"Error inserting/updating data into MySQL: {error}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def extract_client_details(self):
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )

            with conn.cursor() as cursor:
                cursor.execute("SELECT client_id,email_id,password,client "
                               "FROM client WHERE client ='Della1' ")
                result = cursor.fetchone()

                if result:
                    return result
                else:
                    return None

        except mysql.connector.Error as error:
            print(f"Error connecting to MySQL: {error}")

        finally:
            if conn.is_connected():
                conn.close()

    def email_data_information(self):

        labels = "Client"
        vms_data = self.extract_client_details()
        unread_emails = get_unread_emails(vms_data[1], vms_data[2], labels)

        extracted_results = []
        date_received = ''
        result = {}

        for email_data in unread_emails:
            date_received = email_data['date_received'].strftime("%Y-%m-%d %H:%M:%S")
            email_body = email_data['body']

            lines = email_body.split('\n')
            result = {}
            for line in lines:
                if line.startswith("Job Name:"):
                    result["job_title"] = line.split("Job Name:", 1)[1]
                elif line.startswith("Job ID:"):
                    result["client_job_id"] = line.split("Job ID:", 1)[1]
                elif line.startswith("Job Location:"):
                    result["location"] = line.split("Job Location:", 1)[1]
                elif line.startswith("Job Start Date:"):
                    result["job_start_date"] = line.split("Job Start Date: ", 1)[1]
                elif line.startswith("Job End Date:"):
                    result["job_end_date"] = line.split("Job End Date:", 1)[1]
                elif line.startswith("Target Rate:"):
                    result["job_bill_rate"] = line.split("Target Rate:", 1)[1].replace("$","")
            if "Job Description :" in email_body:
                result["job_description"] = email_body.split("Job Description :", 1)[1].split("Thank you,", 1)[0]


            if all(result.values()):
                extracted_results.append(result)

            formatted_results = []
            for result in extracted_results:
                formatted_result = {
                    'job_title': result.get("job_title", ""),
                    'client_job_id': result.get("client_job_id", ""),
                    'location': result.get("location", ""),
                    'job_start_date': result.get("job_start_date", ""),
                    'job_end_date': result.get("job_end_date", ""),
                    'job_bill_rate': result.get("job_bill_rate", ""),
                    'job_description': result.get("job_description", ""),
                    "client": vms_data[3],
                    "client_id": vms_data[0],
                }
                formatted_results.append(formatted_result)

            self.insert_data_into_mysql(formatted_results)
            return formatted_results



my_instance = client_mail_extraction()
my_instance.email_data_information()


