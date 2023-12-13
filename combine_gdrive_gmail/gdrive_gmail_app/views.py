import email
import imaplib
from email.header import decode_header
from email.utils import parsedate_to_datetime
import html2text
import io
import fitz  # PyMuPDF
from django.shortcuts import render
from gdrive_gmail_app import models, serializers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from concurrent import futures

class Getname_details(GenericAPIView):
    serializer_class = serializers.User_email
    queryset = models.UserDetails

    def post(self, request):
        try:
            user_email = request.data.get('user_email')
            query_set = models.UserDetails.objects.filter(user_email=user_email)
            serializer_class = serializers.ass_serial(query_set, many=True)
            source_ids = [item.strip() for entry in serializer_class.data for item in entry.get('source_ids').split(',')]
            subjects_from_db = [item.strip() for entry in serializer_class.data for item in entry.get('subject').split(',')]

            # Extracting unread emails
            email_extraction_result = self.extract_unread_emails(user_email, source_ids, subjects_from_db)

            # Adding email extraction result, Source_IDs, and Subjects to the response
            response_data = {
                "user_details": serializer_class.data,
                'source_ids': source_ids,
                'subjects_from_db': subjects_from_db,
                "email_extraction": email_extraction_result
            }

            return Response(response_data)
        except Exception as e:
            return Response(str(e))


    def extract_unread_emails(self, user_email, source_ids, subjects_from_db):
        imapUserEmail = "kiruthika.b@vrdella.com"
        imapPassword = "renm kixf nlxy avbx"
        imap_server = "imap.gmail.com"
        imap_port = 993
        imap_conn = imaplib.IMAP4_SSL(imap_server, imap_port)

        try:
            imap_conn.login(imapUserEmail, imapPassword)
            imap_conn.select('inbox')

            emails = []

            for source_id, subject_from_db in zip(source_ids, subjects_from_db):
                _, message_ids = imap_conn.search(None, f'FROM "{source_id}" SUBJECT "{subject_from_db}" UNSEEN')

                for message_id in message_ids[0].split():
                    try:
                        _, data = imap_conn.fetch(message_id, "(RFC822)")
                        raw_email = data[0][1]
                        email_message = email.message_from_bytes(raw_email)

                        subject = email_message["Subject"]
                        sender = email.utils.parseaddr(email_message["From"])[0]
                        body1 = ""
                        attachments = []

                        date_received = parsedate_to_datetime(email_message["Date"])

                        if email_message.is_multipart():
                            for part in email_message.walk():
                                if part.get_content_type() == "text/plain":
                                    body1 = part.get_payload(decode=True).decode(errors='replace')
                                elif part.get_content_type() == "text/html":
                                    body1 = html2text.html2text(part.get_payload(decode=True).decode(errors='replace'))
                                elif part.get_content_maintype() != 'multipart' and part.get(
                                        'Content-Disposition') is not None:
                                    filename = part.get_filename()
                                    if filename:
                                        filename, encoding = decode_header(filename)[0]
                                        if isinstance(filename, bytes):
                                            filename = filename.decode(encoding or "utf-8", errors='replace')
                                        attachment_data = part.get_payload(decode=True)
                                        attachments.append({
                                            "filename": filename,
                                            "data": self.extract_text_from_pdf(attachment_data)
                                        })

                        email_data = {
                            "subject": subject,
                            "sender": sender,
                            "body": body1,
                            "date_received": date_received,
                            "email_id": message_id,
                            "attachments": attachments
                        }

                        emails.append(email_data)
                    except Exception as e:
                        print(f"Error processing email: {str(e)}")
                        imap_conn.store(message_id, '+FLAGS', '(\Seen)')

        finally:
            imap_conn.close()

        return emails

    def extract_text_from_pdf(self, pdf_data):
        pdf_document = fitz.open(stream=io.BytesIO(pdf_data), filetype="pdf")
        text_content = ""
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            text_content += page.get_text()
        return text_content

