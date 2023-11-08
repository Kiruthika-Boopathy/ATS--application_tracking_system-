from fpdf import FPDF
details={
  'full_name': 'Donna Johnson',
  'first_name': 'Donna',
  'last_name': 'Johnson',
  'date_of_birth': 'N/A',
  'position': 'NOC Systems Desktop Specialist',
  'description': 'To secure a position that will utilize my computer skills and management experience offering opportunity for professional growth in a dynamic environment.',
  'email_id': 'Donna62John@yahoo.com',
  'mobile_number': '470-213-4277',
  'location': 'Duluth, GA 30096',
  'education': [
    {
      'school_or_college': 'Brevard County Community College',
      'course_name': 'Computer Repair Technology',
      'years': 'N/A'
    }
  ],
  'interests': 'N/A',
  'speaking_languages': 'N/A',
  'work_experience': [
    {
      'position': 'NOC Systems Desktop Specialist',
      'years': '4/14-8/27/19',
      'company': 'Milner Technology Services',
      'domain': 'N/A'
    },
    {
      'position': 'IT Desktop Support Specialist',
      'years': '5/12-12/20/13',
      'company': 'IBM (Contracting through Artech)',
      'domain': 'N/A'
    },
    {
      'position': 'IT Desktop Support Specialist',
      'years': '9/11-12/11',
      'company': 'Pima County (Yoh | A Day & Zimmermann Company)',
      'domain': 'N/A'
    },
    {
      'position': 'IT Desktop Support Specialist',
      'years': '5/11-7/11',
      'company': 'Sun Trust Bank (Contracted through APEX)',
      'domain': 'N/A'
    },
    {
      'position': 'Helpdesk Coordinator',
      'years': '2/11-4/11',
      'company': 'CDC (Contracted with TekSystems)',
      'domain': 'N/A'
    },
    {
      'position': 'IT Desktop Support Specialist',
      'years': '6/10-7/10',
      'company': 'John Deere (short term contract through United Global)',
      'domain': 'N/A'
    },
    {
      'position': 'Desktop Support Specialist',
      'years': '2/09-10/09',
      'company': 'Forsyth County School Board- Atlanta GA (contracting through Think Resources)',
      'domain': 'N/A'
    },
    {
      'position': 'IT Desktop Support Specialist',
      'years': '6/2005-2/2009',
      'company': 'FUNDtech Corporation- Atlanta GA (contracted through Think Resources 7/05-2/06)',
      'domain': 'N/A'
    },
    {
      'position': 'Corporate Support Helpdesk Center Specialist',
      'years': '10/03-7/04',
      'company': 'Blue Cross Blue Shield of Alabama- Birmingham, AL (Contracted through Comforce for six months)',
      'domain': 'N/A'
    },
    {
      'position': 'Computer Repair Technician',
      'years': '10/02-3/03',
      'company': 'CompUSA- Birmingham, AL',
      'domain': 'N/A'
    },
    {
      'position': 'Distributed Computer Support Specialist',
      'years': '4/98-3/2002',
      'company': 'Brevard County Clerk of Courts- Titusville, FL',
      'domain': 'N/A'
    },
    {
      'position': 'Information Technology Technician',
      'years': '2/96-4/98',
      'company': 'Central Data Computer Center- Titusville, FL',
      'domain': 'N/A'
    },
    {
      'position': 'Lead Technician',
      'years': '4/85-7/95',
      'company': 'McDonnell-Douglas Inc- Titusville FL',
      'domain': 'N/A'
    }
  ],
  'certificates': [
    'Microsoft A+ Certified',
    'HP, Compaq, Dell, IBM warranty certifications'
  ],
  'achievements': [
    'Dean’s list-Vocational certificate: Computer Repair Technology',
    'Employee of the month award'
  ],
  'skills': 'A+ Certified Information Technology professional, MS Windows support, MS Servers, LAN Administration, Helpdesk support, troubleshooting, Dell, IBM/Lenova, HP desktops, laptops, printers, switches, peripherals, TCPIP, DNS, VPN',
  'projects_list': 'N/A',
  'years_of_experience': 'N/A',
  'current_position': 'NOC Systems Desktop Specialist',
  'current_company': 'Milner Technology Services',
  'current_company_domain': 'N/A',
  'current_company_business': 'N/A',
  'previous_company': 'IBM (Contracting through Artech)',
  'previous_domain_worked_history': 'N/A',
  'work_authorization': 'N/A',
  'clearance': 'N/A',
  'address': '1060 Court Drive Apt. S, Duluth, GA 30096,',
  'disability': 'N/A',
  'patents_info': 'N/A',
  'primary_skills': 'A+ Certified Information Technology professional, MS Windows support, MS Servers, LAN Administration, Helpdesk support, troubleshooting, Dell, IBM/Lenova, HP desktops, laptops, printers, switches, peripherals, TCPIP, DNS, VPN',
  'social_media_id': 'N/A',
  'linkedin_url': 'N/A',
  'extra_activities': 'N/A',
  'job_title': 'NOC Systems Desktop Specialist',
  'city': 'Duluth',
  'state': 'GA',
  'skype_id': 'N/A',
  'facebook_profile_url': 'N/A',
  'twitter_profile_url': 'N/A',
  'ownership': 'N/A',
  'expected_pay': 'N/A',
  'relocation': 'N/A',
  'technology': 'N/A',
  'race_ethnicity': 'N/A',
  'willingness_to_relocate': 'N/A'
}

class PDF(FPDF):
  def header(self):
    if self.page_no() == 1:
      self.set_font('Arial', 'B', 12)
      self.cell(0, 20, 'Candidate Resume', 0, 1, 'C')

  def footer(self):
    self.set_y(-15)
    self.set_font('Arial', 'I', 8)
    self.cell(0, 10, 'Page %s' % self.page_no(), 0, 0, 'C')

  def add_details(self,details):
    self.set_font('Arial', 'B', 12)
    full_name = details['first_name'] + ' ' + details['last_name']
    self.cell(0, 8, full_name, ln=True)
    self.set_font('Arial', '', 10)
    self.cell(0, 6, details['position'], ln=True)
    self.cell(0, 6, details['location'], ln=True)
    self.cell(0, 6, details['email_id'], ln=True)
    self.cell(0, 6, details['mobile_number'], ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Summary', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['description'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Education', ln=True)
    self.set_font('Arial', '', 10)
    for education in details['education']:
      self.cell(0, 6, "Institute/School : " + education['school_or_college'], ln=True)
      self.cell(0, 6, "Course Name : " + education['course_name'], ln=True)
      self.cell(0, 6, "Duration : " + education['years'], ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Skills', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['skills'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Work Experience', ln=True)
    self.ln(3)
    self.set_font('Arial', '', 10)
    for experience in details['work_experience']:
      self.set_font('Arial', 'BU', 12)
      self.cell(0, 6, "Position : " + experience['position'], ln=True)
      self.set_font('Arial', '', 10)
      self.cell(0, 6, "Years : " + experience['years'], ln=True)
      self.cell(0, 6, "Company : " + experience['company'], ln=True)
      self.cell(0, 6, "Domain : " + experience['domain'], ln=True)
      self.ln(4)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Interests:', ln=True)
    self.set_font('Arial', '', 10)
    self.cell(0, 6, details['interests'], ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Speaking_languages:', ln=True)
    self.set_font('Arial', '', 10)
    self.cell(0, 6, details['speaking_languages'], ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Certificates', ln=True)
    self.set_font('Arial', '', 10)
    for certificates in details['certificates']:
      self.multi_cell(0, 5, certificates)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'achievements', ln=True)
    self.set_font('Arial', '', 10)
    for achievement in details['achievements']:
      self.multi_cell(0, 5, achievement.replace('’', ''))

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Projects_list', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['projects_list'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Years_of_experience:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['years_of_experience'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Current_position:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['current_position'])

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Current_company:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    self.multi_cell(0, 5, details['current_company'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Current_company_domain:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['current_company_domain'])

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Current_company_business:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    self.multi_cell(0, 5, details['current_company_business'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'previous_company:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['previous_company'])

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'previous_domain_worked_history:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    self.multi_cell(0, 5, details['previous_domain_worked_history'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'work_authorization:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['work_authorization'])

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'clearance:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    self.multi_cell(0, 5, details['clearance'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'address:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['address'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'disability:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['disability'])

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'patents_info:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    self.multi_cell(0, 5, details['patents_info'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'primary_skills:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['primary_skills'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'extra_activities:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['extra_activities'])

    self.ln(5)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'job_title:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['job_title'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'city:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['city'])

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'state:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    self.multi_cell(0, 5, details['state'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'social_media_id:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['social_media_id'])

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'skype_id:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    self.multi_cell(0, 5, details['skype_id'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'ownership:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['ownership'])

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'linkedin_url:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    self.multi_cell(0, 5, details['linkedin_url'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'expected_pay:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['expected_pay'])

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'facebook_profile_url:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    self.multi_cell(0, 5, details['facebook_profile_url'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'technology:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['technology'])

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'twitter_profile_url:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    self.multi_cell(0, 5, details['twitter_profile_url'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'relocation:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['relocation'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'willingness_to_relocate:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['willingness_to_relocate'])

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'race_ethnicity:', ln=True)
    self.set_font('Arial', '', 10)
    self.multi_cell(0, 5, details['race_ethnicity'])

pdf = PDF()
pdf.add_page()
pdf.add_details(details)
pdf.output('resume.pdf')





