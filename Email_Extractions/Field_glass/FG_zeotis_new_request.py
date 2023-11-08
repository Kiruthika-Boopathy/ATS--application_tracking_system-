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
    'database': 'email_extraction'
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
    def insert_into_mysql(self,formatted_results):
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'])

            cursor = conn.cursor()

            for result_data in formatted_results:
                cursor.execute(
                    "SELECT COUNT(*) FROM client_data WHERE client_job_id = %s",
                    (result_data['client_job_id'],)
                )
                record_count = cursor.fetchone()[0]

                if record_count == 0:
                    insert_query = """ INSERT INTO client_data 
                                    (
                                        client_job_id,
                                        job_title,
                                        location,
                                        buisness_unit,
                                        job_start_date,
                                        job_end_date,
                                        no_of_positions,
                                        job_description,
                                        client_id,
                                        client,
                                        job_id,
                                        Client_name
                                    )
                                    VALUES
                                    (
                                     %(client_job_id)s,
                                     %(job_title)s,
                                     %(location)s,
                                     %(buisness_unit)s,
                                     %(job_start_date)s,
                                     %(job_end_date)s,
                                     %(no_of_positions)s,
                                     %(job_description)s,
                                     %(client_id)s,
                                     %(client)s,
                                     %(job_id)s,
                                     %(Client_name)s
                                     )"""

                    data_to_insert = {
                        "client_job_id": result_data['client_job_id'],
                        "Client_name": result_data['Client_name'],
                        "job_title": result_data['job_title'],
                        "client_id": result_data['client_id'],
                        "client": result_data['client'],
                        "job_id": str(uuid.uuid4()),
                        "location": result_data['location'],
                        "buisness_unit": result_data['buisness_unit'],
                        "job_start_date": result_data['job_start_date'],
                        "job_end_date": result_data["job_end_date"],
                        "no_of_positions": result_data["no_of_positions"],
                        "job_description": result_data["job_description"]



                    }
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                    cursor.execute(insert_query , data_to_insert)
            conn.commit()
            print("successfully inserted")
            return cursor.fetchall()

        except mysql.connector.Error as error:
            print(f"Error inserting data into MySQL: {error}")

        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def update_into_mysql(self,formatted_results):

        try:
            conn = mysql.connector.connect(host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'])
            cursor = conn.cursor()

            for result_data in formatted_results:

                update_query = """ UPDATE client_data SET job_status = %(job_status)s,comment =   %(comment)s 
                                WHERE client_job_id = %(client_job_id)s"""



                data_to_insert = {"client_job_id": result_data['client_job_id'],
                                  "comment": result_data['comment'],
                                  "job_status": result_data['job_status'],}



                cursor.execute(update_query ,data_to_insert)
            conn.commit()
            print("successfully updated")
            return "successfully updated"

        except mysql.connector.Error as error:
            print(f"Error inserting data into MySQL: {error}")

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
                cursor.execute("SELECT client_id, email_id, password, client FROM client WHERE client = 'Zeotis'")
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

    def update_data_information(self,unread_emails):
        for email_data in unread_emails:
            if 'body' in email_data:
                email_body = email_data['body']
                email_subject = email_data["subject"]
                # print(email_body)

                result = {}
                extracted_results = []
                if "### Requisition ID" in email_body:
                    result["client_job_id"]=email_body.split("### Requisition ID",1)[1].split("--- ",1)[0].replace("\n","").replace(" ",'')
                if "### Comments To Supplier" in email_body:
                    result["comment"]=email_body.split("### Comments To Supplier",1)[1].split("---",1)[0].replace("\n","").replace(" ",'')
                if "halted" in email_subject:
                    result["job_status"]= "closed"

                if all(result.values()):
                    extracted_results.append(result)

                formatted_results = []
                formatted_result={}
                for result in extracted_results:
                    formatted_result = {
                        "client_job_id" : result.get("client_job_id"," "),
                        "job_status" : result.get("job_status"," "),
                        "comment" : result.get("comment"," ")
                        }
                formatted_results.append(formatted_result)
                self.update_into_mysql(formatted_results)

                return  formatted_results

    def insert_data_information(self):
        labels = "field_glass"
        vms_data = self.extract_client_details()
        unread_emails = get_unread_emails(vms_data[1], vms_data[2], labels)
        extracted_results = []
        formatted_results = []
        result = {}
        for email_data in unread_emails:
            email_body = email_data["body"]
            email_subject = email_data["subject"]
            # print(email_body)

            if "### Requisition ID" in email_body:
                result["client_job_id"] = email_body.split("### Requisition ID", 1)[1].split("---", 1)[0].replace('\n',
                                                                                                                  '').replace(' ', '')
            if "### Requisition Title":
                result["job_title"] = email_body.split("### Requisition Title", 1)[1].split("### Site", 1)[0].replace('\n', '').replace(' ', '')

            if "### Site" in email_body:
                result["location"] = email_body.split("### Site", 1)[1].split("### Business Unit", 1)[0].replace('\n','').replace(' ', '')

            if "### Business Unit" in email_body:
                result["buisness_unit"] = email_body.split("### Business Unit", 1)[1].split("### Requisition Start Date",1)[0].replace('\n','').replace(' ', '')

            if "### Requisition Start Date" in email_body:
                result["job_start_date"] = email_body.split("### Requisition Start Date", 1)[1].split("### Requisition End Date", 1)[0].replace('\n', '').replace(' ', '')

            if "### Requisition End Date" in email_body:
                result["job_end_date"] = email_body.split("### Requisition End Date", 1)[1].split('### Requisition Number of Positions', 1)[0].replace('\n', '').replace(' ', '')

            if "### Requisition Number of Positions" in email_body:
                result["no_of_positions"] = email_body.split("### Requisition Number of Positions", 1)[1].split("### Description", 1)[0].replace('\n', '').replace(' ', '')

            if "### Description" in email_body:
                result["job_description"] = email_body.split("### Description", 1)[1].split("## Accounting", 1)[0].replace('\n', '').replace(' ', '')

            if all(result.values()):
                extracted_results.append(result)


            for result in extracted_results:
                formatted_result = {
                    "client_job_id": result.get("client_job_id", " "),
                    "job_title": result.get("job_title", " "),
                    "location": result.get("location", " "),
                    "buisness_unit": result.get("buisness_unit", " "),
                    "job_start_date": result.get("job_start_date", " "),
                    "job_end_date": result.get("job_end_date", " "),
                    "no_of_positions": result.get("no_of_positions", " "),
                    "job_description": result.get("job_description", " "),
                    "client_id": vms_data[0],
                    "client": vms_data[3],
                    "Client_name": "Zeotis"
                }
                formatted_results.append(formatted_result)
                if "New Requisition" in email_subject:
                    self.insert_into_mysql(formatted_results)

                if "Requisition halted" in email_subject:
                    self.update_data_information(unread_emails)

                return formatted_results


my_instance = extract_and_insert()
my_instance.insert_data_information()