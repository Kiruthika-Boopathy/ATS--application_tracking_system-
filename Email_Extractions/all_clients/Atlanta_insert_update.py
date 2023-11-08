import imaplib
import email
from datetime import datetime
import html2text
import mysql.connector
import uuid


db_config = {
    "host": "localhost",
    "user": "root",
    "password": "vrdella!6",
    "database": "email_extraction",
}

def get_unread_emails(email_address, password, label):
    imap_server = "imap.gmail.com"
    imap_port = 993

    imap_conn = imaplib.IMAP4_SSL(imap_server, imap_port)

    imap_conn.login(email_address, password)

    labels = label
    imap_conn.select(labels)
    unread_emails = []

    _, message_ids = imap_conn.search(None, "(UNSEEN)")

    for message_id in message_ids[0].split():
        _, data = imap_conn.fetch(message_id, "(RFC822)")
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)

        subject = email_message["Subject"]
        sender = email.utils.parseaddr(email_message["From"])[1]
        body1 = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)

                if content_type == "text/plain":
                    if payload is not None:
                        body1 = payload.decode()
                elif content_type == "text/html":
                    if payload is not None:
                        body1 = html2text.html2text(payload.decode())

        else:
            payload = email_message.get_payload(decode=True)
            if payload is not None:
                body1 = payload.decode()

        email_data = {
            "subject": subject,
            "sender": sender,
            "body": body1
        }

        unread_emails.append(email_data)

    imap_conn.close()

    return unread_emails


class email_extract():


    def insert_data_into_mysql(self, extracted_results):
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            cursor = conn.cursor()

            for result_data in extracted_results:

                cursor.execute(
                    "SELECT COUNT(*) FROM client_data WHERE client_job_id = %s",
                    (result_data['client_job_id'],)
                )
                record_count = cursor.fetchone()[0]

                if record_count == 0:
                    insert_query = """
                        INSERT INTO client_data (
                                                client_job_id,
                                                Client_name,
                                                job_title,
                                                client_id,
                                                client,
                                                job_id

                                        ) VALUES (
                                                %(client_job_id)s,
                                                %(Client_name)s,
                                                %(job_title)s,
                                                %(client_id)s,
                                                %(client)s,
                                                %(job_id)s
                                            )
                    """

                    data_to_insert = {
                        "client_job_id": result_data['client_job_id'],
                        "Client_name": result_data['Client_name'],
                        "job_title": result_data['job_title'],
                        "client_id": result_data['client_id'],
                        "client": result_data['client'],
                        "job_id": str(uuid.uuid4())
                    }
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                    cursor.execute(insert_query, data_to_insert)

            conn.commit()
            print("successfully inserted")
            return cursor.fetchall()

        except mysql.connector.Error as error:
            print(f"Error inserting data into MySQL: {error}")

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()


    def update_data_in_mysql(self, formatted_results):
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            cursor = conn.cursor()

            for result_data_item in formatted_results:
                update_query = """ UPDATE client_data
                                   SET
                                      comment = %(comment)s,
                                      job_status = %(job_status)s
                                                           WHERE client_job_id = %(client_job_id)s"""

                data_to_update = {

                    "comment": result_data_item.get('comment', None),
                    "job_status":result_data_item.get("job_status",None),
                    "client_job_id": result_data_item['client_job_id']
                }

                cursor.execute(update_query, data_to_update)

            conn.commit()
            return "Data updated successfully"
        except mysql.connector.Error as error:
            print(f"Error updating data in MySQL: {error}")
        finally:
            if conn is not None and conn.is_connected():
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
                cursor.execute("SELECT client_id, email_id, password, client FROM client WHERE client = 'Atlanta1'")
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

    def update_email_data(self,unread_emails):



        extracted_results = []

        result = {}

        for email_data in unread_emails:

            email_subject = email_data['subject']
            lines = email_subject.split("\n")
            for line in lines:
                if "not accepting new proposals" in email_subject:

                    if "Requisition" in line:
                        result["client_job_id"] = line.split("Requisition", 1)[1].split("is", 1)[0].replace(" ", '')

                    email_body = email_data["body"]
                    lines1 = email_body.split("\n")
                    for line1 in lines1:
                        if line1.startswith("Requisition Name/ID:"):
                            result["job_title"] = line1.split("Requisition Name/ID:", 1)[1].split("/", 1)[0]
                        elif line1.startswith("Information"):
                            result["comment"] = line1
                    result["job_status"] = "not accepted"

                elif "Filled" in email_subject:
                    for line in lines:
                        if "Requisition" in line:
                            result["client_job_id"] = line.split("Requisition", 1)[1].split("has", 1)[0].replace(" ",
                                                                                                                 '')

                    email_body = email_data["body"]
                    lines1 = email_body.split("\n")
                    for line1 in lines1:
                        if line1.startswith("Requisition Name/ID:"):
                            result["job_title"] = line1.split("Requisition Name/ID:", 1)[1].split("/", 1)[0]
                    if "The requisition has been filled." in email_body:
                        result["comment"] = email_body.split("The requisition has been filled.", 1)[1].split("Customer", 1)[0]
                    result["job_status"] = "closed"





        if all(result.values()):
            extracted_results.append(result)

        formatted_results = []
        for result in extracted_results:
            formatted_result = {
                'client_job_id': result.get("client_job_id", ""),
                'job_title': result.get("job_title", ''),
                'comment': result.get("comment", ''),
                'job_status': result.get("job_status", ''),

            }
            formatted_results.append(formatted_result)
            print(formatted_results)

        self.update_data_in_mysql(formatted_results)
        return formatted_results







    def email_data_information(self):
        global extracted_results
        labels = "Atlanta1"
        vms_data = self.extract_client_details()

        unread_emails = get_unread_emails(vms_data[1], vms_data[2], labels)

        for email_data in unread_emails:
            email_body = email_data["body"]
            email_subject = email_data["subject"]
            extracted_results=[]
            result ={}
            lines = email_body.split("\n")
            for line in lines:
                if line.startswith("Atlanta"):
                    result["Client_name"] = line.split(",", 1)[0].strip()
                elif line.startswith("Field Tech (Desk Side)"):
                    result["job_title"] = line.split("Field Tech (Desk Side)", 1)[1].split(".", 1)[0].strip()
                elif line.startswith("3\."):
                    result["client_job_id"] = line.split("-", 1)[1].strip()

            formatted_result = {

                "job_title": result.get("job_title", ""),
                "client_job_id": result.get("client_job_id", ""),
                "Client_name":result.get("Client_name",""),
                "client_id":vms_data[0],
                "client":vms_data[3]
            }

            extracted_results.append(formatted_result)
            if "has been posted" in email_subject:
                self.insert_data_into_mysql(extracted_results)
            if "not accepting new proposals" or "has been Filled":
                self.update_email_data(unread_emails)



        return extracted_results

extracted_results = email_extract()
extracted_results.email_data_information()