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


class client_mail_extraction:

    def insert_data_into_mysql(self, formatted_results1):
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            cursor = conn.cursor()

            for result_data_item in formatted_results1:
                cursor.execute(
                    "SELECT COUNT(*) FROM client_data WHERE client_job_id = %s",
                    (result_data_item['client_job_id'],)
                )
                record_count = cursor.fetchone()[0]

                if record_count == 0:
                    insert_query = """
                    INSERT INTO client_data(
                        job_title,
                        client_job_id,
                        job_start_date,
                        job_end_date,
                        job_bill_rate,
                        location,
                        client_name,
                        client_id,
                        no_of_positions,
                        job_description,
                        job_id
                    ) VALUES (
                        %(job_title)s,
                        %(client_job_id)s,
                        %(job_start_date)s,
                        %(job_end_date)s,
                        %(job_bill_rate)s,
                        %(location)s,
                        %(client_name)s,
                        %(client_id)s,
                        %(no_of_positions)s,
                        %(job_description)s,
                        %(job_id)s
                    )
                    """
                    data_to_insert = {
                        "job_title": result_data_item['job_title'],
                        "client_job_id": result_data_item['client_job_id'],
                        "job_start_date": result_data_item['job_start_date'],
                        "job_end_date": result_data_item['job_end_date'],
                        "job_bill_rate": result_data_item['job_bill_rate'],
                        "location": result_data_item['location'],
                        "client_name": result_data_item['client_name'],
                        "client_id": result_data_item['client_id'],
                        "no_of_positions": result_data_item['no_of_positions'],
                        "job_description": result_data_item['job_description'],
                        "job_id": str(uuid.uuid4())
                    }

                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                    cursor.execute(insert_query, data_to_insert)

            conn.commit()
            return "Data inserted successfully"
        except mysql.connector.Error as error:
            print(f"Error inserting data into MySQL: {error}")
        finally:
            if conn is not None and conn. is_connected():
                cursor.close()
                conn.close()

    def update_data_in_mysql(self, formatted_results2):
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            cursor = conn.cursor()

            for result_data_item in formatted_results2:
                update_query = """ UPDATE client_data
                                   SET
                                      comment = %(comment)s
                                                           WHERE client_job_id = %(client_job_id)s"""

                data_to_update = {

                    "comment": result_data_item.get('comment', None),
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
                cursor.execute("SELECT client_id,email_id,password,client_name "
                               "FROM client WHERE client_name = 'supplier'")
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

    def update_logic_data(self,unread_emails):

        extracted_results = []
        for email_data in unread_emails:
            email_body = email_data['body']
            print(email_body)
            lines = email_body.split('\n')
            result = {}

            for line in lines:
                line = line.strip()

                if line.startswith("23-00179"):
                    result["id"] = line.strip("__ __")
                elif line.startswith("Controls Engineer __ __"):
                    result["title"] = line.strip("__ __")
                elif line.startswith("1 __ __"):
                    result["position"] = line.strip("__ __")
                elif line.startswith("Seattle"):
                    result["location"] = line.strip("__ __")
                elif line.startswith("HOLD"):
                    result["priority"] = line.strip("__ __")
            if "Please" in email_body:
                result["notes"] = email_body.split("HOLD __ __", 1)[1].split("23-00168", 1)[0].replace("__ __",
                                                                                                       '').replace("|",
                                                                                                                   '')

        if all(result.values()):
            extracted_results.append(result)

        formatted_results2 = []
        for result in extracted_results:
            job_title = result.get("title", None)
            client_job_id = result.get("id", None)
            location = result.get("job_location", None)
            no_of_positions = result.get("position", None)
            comment = result.get("notes", None)

            formatted_result = {
                "job_title": job_title,
                "client_job_id": client_job_id,
                "location": location,
                "no_of_positions": no_of_positions,
                "comment": comment

            }
            formatted_results2.append(formatted_result)
        print(formatted_results2)

        result = self.update_data_in_mysql(formatted_results2)
        print("Insert Result:", result)
        return result

    def email_data_information(self):
        labels = "supplier"
        vms_data = self.extract_client_details()
        unread_emails = get_unread_emails(vms_data[1], vms_data[2], labels)

        extracted_results = []
        date_received = ''
        result = {}

        for email_data in unread_emails:
            email_body = email_data['body']
            email_subject = email_data['subject']
            lines = email_body.split('\n')
            result = {}

            for line in lines:
                if "**Ref No" in email_body:
                    result["Ref_no"] = email_body.split("**Ref No", 1)[1].split("]", 1)[0].replace("*", '').replace("[",'').strip(":").strip("\n")
                if "**Title" in line:
                    result["job_title"] = line.split("**Title", 1)[1].strip(":**")
                elif "**Start Date" in line:
                    result["start_date"] = line.split("**Start Date", 1)[1].strip(":**")
                elif "**End Date" in line:
                    result["end_date"] = line.split("**End Date", 1)[1].strip(":**")
                elif "**Bill Rate" in line:
                    result["bill_rate"] = line.split("**Bill Rate", 1)[1].strip(":**").replace("$", '')
                elif "**# of Openings" in line:
                    result["of_openings"] = line.split("**# of Openings", 1)[1].strip(":**")
                elif "**Position Type" in line:
                    result["position_type"] = line.split("**Position Type", 1)[1].strip(":**")
                elif "**Locations" in line:
                    result["location"] = line.split("**Locations", 1)[1].strip(":**")
            if "**Description" in email_body:
                result["description"] = email_body.split("**Description", 1)[1].strip(":**")

        if all(result.values()):
            extracted_results.append(result)

        formatted_results1 = []
        for result in extracted_results:
            formatted_result = {
                "client_job_id": result.get("Ref_no", None),
                "job_title": result.get("job_title", None),
                "job_start_date": result.get("start_date", None),
                "job_end_date": result.get("end_date", None),
                "job_bill_rate": result.get("bill_rate", None),
                "no_of_positions": result.get("of_openings", None),
                "location": result.get("location", None),
                "job_description": result.get("description", None),
                "client_name": vms_data[3],
                "client_id": vms_data[0],

            }
        formatted_results1.append(formatted_result)
        if "assigned" in email_subject:
            result = self.insert_data_into_mysql(formatted_results1)
        if 'Update' in email_subject:
             result = self.update_logic_data(unread_emails)

        return result


my_instance = client_mail_extraction()
insertion_result = my_instance.email_data_information()




