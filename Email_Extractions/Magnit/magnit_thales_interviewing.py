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
                client_jobid = result.get("client_jobid", None)
                first_name = result.get("first_name", None)
                comments = result.get("comments", None)

                cursor.execute("SELECT job_id FROM jobpostings WHERE client_jobid = %s", (client_jobid,))
                job_id = cursor.fetchone()[0]

                if job_id:
                    result["job_id"] = job_id

                else:
                    print("client_jobid  not found in the database.")

                cursor.execute("SELECT applicants_id FROM applicants WHERE first_name = %s", (first_name,))
                applicants_id = cursor.fetchone()[0]

                if applicants_id:
                    result["applicants_id"] = applicants_id

                else:
                    print("first_name not found in the database.")

                cursor.execute("SELECT * FROM applicant_progress_status WHERE job_id = %s AND applicants_id = %s",
                               (job_id, applicants_id))
                existing_record = cursor.fetchone()

                if existing_record:
                    update_query = """UPDATE applicant_progress_status 
                                          SET comments = %s,
                                          candidates_status = JSON_SET(
                                                 candidates_status,
                                                 '$.interviewing',
                                                 CASE WHEN JSON_UNQUOTE(JSON_EXTRACT(candidates_status, '$.rejected')) = 'false' THEN 'true' ELSE 'false' END)
                                         WHERE job_id = %s AND applicants_id = %s;"""
                    data_to_update = (comments, job_id, applicants_id)

                    cursor.execute(update_query, data_to_update)
                    conn.commit()
                    result["comments"] = comments

                    print(
                        f"Successfully updated comments and candidates_status for job_id = {job_id} and applicants_id = {applicants_id}")
                else:
                    print(f"Job_id {job_id} and applicants_id {applicants_id} not found in the database.")


        except mysql.connector.Error as error:
            print(f"Error connecting to the database: {error}")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def email_data_information(self):
        imapUserEmail = "kiruthika.b@vrdella.com"
        imapPassword = "renm kixf nlxy avbx"
        labels = "Magnito"



        unread_emails = get_unread_emails(imapUserEmail, imapPassword, labels)
        for email_data in unread_emails:
            email_body = email_data["body"]
            email_subject = email_data["subject"]
            # print(email_body)
            Lines = email_body.split("\n")

            extracted_results = []
            result = {}
            comments = []
            for line in Lines:
                if line.startswith("ANU"):
                    result["first_name"] = line.split("has", 1)[0].strip(" ")
                if line.startswith("#"):
                    result["client_jobid"] = line.split("#", 1)[1].split("for", 1)[0].strip(" ")
                if line.startswith("#26697760"):
                    job_title = line.split("the", 1)[1].strip(" ")
                    comments.append("job_title:" + job_title)
                elif line.startswith("Date"):
                    date = line.split(":", 1)[1].strip(" ")
                    comments.append("date:" + date)
                elif line.startswith("Time"):
                    time = line.split(":", 1)[1].strip(" ")
                    comments.append("time:" + time)
                elif line.startswith("Duration"):
                    duration = line.split(":", 1)[1].strip(" ")
                    comments.append("duration:" + duration)
                elif line.startswith("Mode"):
                    interview_mode = line.split(":", 1)[1].strip(" ")
                    comments.append("Mode:" + interview_mode)
                elif line.startswith("["):
                    managet_to_invite_link = line.strip(" ")
                    comments.append("managet_to_invite_link:" + managet_to_invite_link)
                elif line.startswith("Type"):
                    interview_type = line.split(":", 1)[1].strip(" ")
                    comments.append("interview_type:" + interview_type)
                elif line.startswith("Interviewers"):
                    interviewers = line.split(":", 1)[1].strip(" ")
                    comments.append("interviewers:" + interviewers)
            if "Notes" in email_body:
                notes = email_body.split("Notes:", 1)[1].split("Regards", 1)[0].strip(" ")
                comments.append("notes:" + notes)

            result["comments"] = " ".join(comments)

            if all(result.values()):
                extracted_results.append(result)

            formatted_results = []
            for result in extracted_results:
                formatted_result = {
                    "first_name": result.get("first_name", " "),
                    "client_jobid": result.get('client_jobid', " "),
                    "comments": result.get("comments", " ")
                }
            formatted_results.append(formatted_result)
            self.insert_into_mysql(formatted_results)

            print(formatted_results)


my_instance = extract_and_insert()
my_instance.email_data_information()