
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
                        Client_name,
                        job_start_date,
                        job_bill_rate,
                        no_of_positions,
                        city,
                        job_description,
                        client,
                        client_id,
                        job_id  -- Add a missing comma
                    ) VALUES (
                        %(job_title)s,
                        %(client_job_id)s,
                        %(Client_name)s,
                        %(job_start_date)s,
                        %(job_bill_rate)s,
                        %(no_of_positions)s,
                        %(city)s,
                        %(job_description)s,
                        %(client)s,
                        %(client_id)s,
                        %(job_id)s
                    )
                    """
                    data_to_insert = {
                        "job_title": result_data_item['job_title'],
                        "client_job_id": result_data_item['client_job_id'],
                        "Client_name": result_data_item['Client_name'],
                        "job_start_date": result_data_item['job_start_date'],
                        "job_bill_rate": result_data_item['job_bill_rate'],
                        "no_of_positions": result_data_item['no_of_positions'],
                        "city": result_data_item['city'],
                        "job_description": result_data_item['job_description'],
                        "client": result_data_item['client'],
                        "client_id": result_data_item['client_id'],
                        "job_id": str(uuid.uuid4())
                    }

                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                    cursor.execute(insert_query, data_to_insert)

            conn.commit()
            print("Data inserted successfully")
            return "Data inserted successfully"
        except mysql.connector.Error as error:
            print(f"Error inserting data into MySQL: {error}")
        finally:
            if conn is not None and conn.is_connected():
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
                cursor.execute("SELECT client_id, email_id, password, client FROM client WHERE client = 'Medifis'")
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

    def update_logic_data(self, unread_emails):
        extracted_results = []
        result = {}
        for email_data in unread_emails:
            email_body = email_data['body']
            email_subject = email_data['subject']
            lines = email_body.split('\n')


            for line in lines:
                line = line.strip()

                if line.startswith("Job Number"):
                    result["client_job_id"] = line.split(":", 1)[1].strip(" ")

            if "Confluence Health Hospital" in email_body:
                result["comments"] = email_body.split("Confluence Health Hospital", 1)[1].split("Job Number", 1)[0]


        extracted_results.append(result)


        formatted_results2 = []
        for result in extracted_results:
            client_job_id = result.get("client_job_id", None)
            comment = result.get("comments", None)

            formatted_result = {
                "client_job_id": client_job_id,
                "comment": comment,
                "job_status": "Filled"
            }
            formatted_results2.append(formatted_result)


        result = self.update_data_in_mysql(formatted_results2)
        print("Insert Result:", result)
        return result

    def email_data_information(self):
        labels = "Medifis"
        vms_data = self.extract_client_details()
        unread_emails = get_unread_emails(vms_data[1], vms_data[2], labels)
        result = {}
        description = []
        extracted_results = []
        email_subject = ''
        formatted_result  = {}

        for email_data in unread_emails:
            email_body = email_data['body']
            email_subject = email_data['subject']
            lines = email_body.split("\n")

            for line in lines:

                if line.startswith("Job Name:"):
                    result["job_title"] = line.split("Job Name:", 1)[1].replace("|", '').replace(" ", '')
                elif line.startswith("Job Order Number:"):
                    result["client_job_id"] = line.split("Job Order Number:", 1)[1].replace("|", '').replace(" ", '')
                elif line.startswith("Client Name:"):
                    result["Client_name"] = line.split("Client Name:", 1)[1].replace("|", '').replace(" ", '')
                elif line.startswith("Number of Positions Available:"):
                    result["no_of_positions"] = line.split("Number of Positions Available:", 1)[1].replace("|", '').replace(" ", '')
                elif line.startswith("Start Date:"):
                    result["job_start_date"] = line.split("Start Date:", 1)[1].replace("|", '').replace(" ", '')
                elif line.startswith("All Inclusive Rate:"):
                    result["job_bill_rate"] = line.split("All Inclusive Rate:", 1)[1].replace("|", '').replace(" ", '')
                elif line.startswith("City:"):
                    result["city"] = line.split("City:", 1)[1].replace("|", '').replace(" ", '')

                elif line.startswith("Facility Name:"):
                    facility_name = line.split("Facility Name:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("facility_name:" + facility_name)
                elif line.startswith("State:"):
                    state = line.split("State:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("state:" + state)
                elif line.startswith("Job Type:"):
                    job_type = line.split("Job Type:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("job_type:" + job_type)
                elif line.startswith("Billing Codes:"):
                    billing_codes = line.split("Billing Codes:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("billing_codes:" + billing_codes)
                elif line.startswith("Specialty:"):
                    speciality = line.split("Specialty:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("speciality:" + speciality)
                elif line.startswith("SubSpecialty:"):
                    sub_speciality = line.split("SubSpecialty:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("sub_speciality:" + sub_speciality)
                elif line.startswith("Minimum Years Experience Required:"):
                    minimum_experience = line.split("Minimum Years Experience Required:", 1)[1].replace("|",
                                                                                                        '').replace(" ",
                                                                                                                    '')
                    description.append("minimum_experience:" + minimum_experience)
                elif line.startswith("Holiday Coverage Required:"):
                    holiday_coverage = line.split("Holiday Coverage Required:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("holiday_coverage:" + holiday_coverage)

                elif line.startswith("Contract Length in weeks:"):
                    contract_length = line.split("Contract Length in weeks:", 1)[1].replace("|", '').replace(" ",
                                                                                                             '')
                    description.append("contract_length:" + contract_length)
                elif line.startswith("Shift:"):
                    shift = line.split("Shift:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("shift:" + shift)

                elif line.startswith("Bilingual:"):
                    billingual = line.split("Bilingual:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("billingual:" + billingual)

                elif line.startswith("H1B Visa Details Required:"):
                    visa_details = line.split("H1B Visa Details Required:", 1)[1].replace("|", '').replace(" ",
                                                                                                           '')
                    description.append("visa_details:" + visa_details)

                elif line.startswith("Position Urgency:"):
                    position_urgency = line.split("Position Urgency:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("position_urgency:" + position_urgency)

                elif line.startswith("Rate Type:"):
                    rate_type = line.split("Rate Type:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("rate_type:" + rate_type)

                elif line.startswith("Incidentals Provided By The Facility:"):
                    incidentals = line.split("Incidentals Provided By The Facility:", 1)[1].replace("|",
                                                                                                    '').replace(
                        " ", '')
                    description.append("incidentals:" + incidentals)


                elif line.startswith("Mileage Reimbursement:"):
                    mileage = line.split("Mileage Reimbursement:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("mileage:" + mileage)
                elif line.startswith("Charge Rate:"):
                    charge_rate = line.split("Charge Rate:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("charge_rate:" + charge_rate)
                elif line.startswith("On Call Rate:"):
                    on_call_rate = line.split("On Call Rate:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("on_call_rate:" + on_call_rate)
                elif line.startswith("Call Back Minimum(Hrs):"):
                    call_back = line.split("Call Back Minimum(Hrs):", 1)[1].replace("|", '').replace(" ", '')
                    description.append("call_back:" + call_back)

                elif line.startswith("Call Back Rate:"):
                    call_back_rate = line.split("Call Back Rate:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("call_back_rate:" + call_back_rate)

                elif line.startswith("Holiday Rate:"):
                    holiday_rate = line.split("Holiday Rate:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("holiday_rate:" + holiday_rate)

                elif line.startswith("Shift Differential:"):
                    shift_diff = line.split("Shift Differential:", 1)[1].replace("|", '').replace(" ", '')
                    description.append("shift_diff:" + shift_diff)

            # Add job_description outside the loop
            result["job_description"] = " ".join(description)

        if all(result.values()):
            extracted_results.append(result)

        formatted_results1 = []
        for result in extracted_results:
                formatted_result = {
                "client_job_id": result.get("client_job_id", None),
                "job_title": result.get("job_title", None),
                "Client_name": result.get("Client_name", None),
                "job_start_date": result.get("job_start_date", None),
                "job_bill_rate": result.get("job_bill_rate", None),
                "no_of_positions": result.get("no_of_positions", None),
                "city": result.get("city", None),
                "job_description": result.get("job_description", None),
                "client": vms_data[3],
                "client_id": vms_data[0],
            }
        formatted_results1.append(formatted_result)

        if "Job Order Notice" in email_subject:
            result = self.insert_data_into_mysql(formatted_results1)
        elif 'Filled' in email_subject:
            result = self.update_logic_data(unread_emails)

        return result


my_instance = client_mail_extraction()
insertion_result = my_instance.email_data_information()
print("success")
