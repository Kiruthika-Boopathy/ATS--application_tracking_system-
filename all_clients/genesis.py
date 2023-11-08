

import uuid
import email
from email.utils import parsedate_to_datetime
import html2text
import mysql.connector
from bs4 import BeautifulSoup
import imaplib as imp

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "vrdella!6",
    "database": "email_extraction",
}


def get_unread_emails(imapUserEmail, imapPassword, label):
    imapHostServer = 'imap.gmail.com'
    imapVar = imp.IMAP4_SSL(imapHostServer)
    imapVar.login(imapUserEmail, imapPassword)
    labels = label
    imapVar.select(labels)
    unread_emails = []
    tmp, data = imapVar.search(None, 'UNSEEN')
    for n in data[0].split():
        typ, msg_data = imapVar.fetch(n, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])

        subject = msg["Subject"]
        sender = email.utils.parseaddr(msg["From"])[1]
        email_text = ""
        for part in msg.walk():
            if part.get_payload(decode=True) is not None:
                body = part.get_payload(decode=True).decode("UTF-8", errors="ignore")
                email_text += body
        date_received = parsedate_to_datetime(msg["Date"])

        email_data = {
            "subject": subject,
            "sender": sender,
            "body": email_text,
            "date_received": date_received
        }

        unread_emails.append(email_data)
    return unread_emails


class genesis_client:

    def insert_data_into_mysql(self, result_dat):
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )
            cursor = conn.cursor()

            for result_data in result_dat:

                cursor.execute(
                    "SELECT COUNT(*) FROM client_data WHERE client_job_id = %s",
                    (result_data['client_job_id'],)
                )
                record_count = cursor.fetchone()[0]

                if record_count == 0:
                    insert_query = """
                        INSERT INTO client_data (
                            client_job_id,
                            job_start_date,
                            job_end_date,
                            location,
                            job_status,
                            client_id,
                            client,
                            
                            job_id
                        ) VALUES (
                            %(client_job_id)s,
                            %(job_start_date)s,
                            %(job_end_date)s,
                            %(location)s,
                            %(job_status)s,
                            %(client_id)s,
                            %(client)s,
                            
                            %(job_id)s
                        )
                    """

                    data_to_insert = {
                        "client_job_id": result_data['client_job_id'],
                        "job_start_date": result_data['job_start_date'],
                        "job_end_date": result_data['job_end_date'],
                        "location": result_data['location'],
                        "job_status": result_data['job_status'],
                        "client_id": result_data['client_id'],
                        "client": result_data['client'],

                        "job_id": result_data['job_id']
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

    def extract_client_details(self):
        try:
            conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database']
            )

            with conn.cursor() as cursor:
                cursor.execute("SELECT client_id, email_id, password, client FROM client WHERE client = 'genesis'")
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

    def genesis_extract_information(self):
        labels = "genesis"
        vms_data = self.extract_client_details()

        # Call the get_unread_emails function to get the list of emails
        unread_emails = get_unread_emails(vms_data[1], vms_data[2], labels)

        extracted_list = []
        result_data = {}

        for email_data in unread_emails:
            # Your email processing code here
            email_body = email_data['body']
            email_subject = email_data['subject']
            soup = BeautifulSoup(email_body, 'html.parser')
            table = soup.find_all('table')

            if table:
                for t in table:
                    table_data = []
                    for row in t.find_all('tr'):
                        row_data = [cell.get_text(strip=True) for cell in row.find_all('td')]
                        table_data.append(row_data)
                        value_data = table_data[-1:][0]
                        html_convertor = html2text.HTML2Text()
                        htmltxt = html_convertor.handle(email_body)
                        a = ''
                        data = htmltxt.split('\n')
                        for i in data:
                            if '#|' in i:
                                a += i
                            if i.startswith('City'):
                                a += i
                        column = ["".join(item.split()) for item in a[3:].split('|')]
                        zip_var = dict(zip(column, value_data))
                        for column, value_data in zip_var.items():
                            if column == 'ShiftDate':
                                if '-' in value_data:
                                    start, end = [date.strip() for date in value_data.split('-')]
                                    zip_var['Start'] = start
                                    zip_var['End'] = end
                        zip_var['State'] = zip_var.get('Area', '') + "," + zip_var.get('City', '') + "," + zip_var.get(
                            "State", '')
                        zip_var["job_id"] = str(uuid.uuid4())
                        date_received = email_data['date_received'].strftime("%Y-%m-%d %H:%M:%S")
                        zip_var['date_received'] = date_received
                        zip_var['job_status'] = 'open'

                        result_data = {
                            "client_job_id": zip_var.get('ID', ''),  # Replace 'client_job_id' with 'ID'
                            "job_start_date": zip_var.get('Start', ''),
                            "job_end_date": zip_var.get('End', ''),
                            "location": zip_var.get('State', ''),
                            "job_status": zip_var.get('job_status', ''),
                            "job_id": zip_var.get('job_id', ''),
                            'client_id': vms_data[0],
                            'client': vms_data[3],

                        }

        extracted_list.append(result_data)
        print(extracted_list)
        result = self.insert_data_into_mysql(extracted_list)
        return extracted_list


results = genesis_client()
results.genesis_extract_information()
