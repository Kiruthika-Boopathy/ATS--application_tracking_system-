import json

from fpdf import FPDF

details={
  "first_name": "Miguel",
  "last_name": "Vega",
  "date_of_birth": "N/A",
  "position": "PTA position",
  "description": "Motivated and caring Physical Therapist Assistant with over 25 years of experience providing quality patient care in various settings. Calm and reassuring personality, with strong communication abilities. Seeking a PTA position with a staff that emphasizes patient health and excellence, where I am able to apply my education, past experiences, and gain knowledge in our respected field.",
  "email_id": "MiguelVegaPTA@Yahoo.com",
  "mobile_number": "813-730-9505",
  "location": "Plant City, FL",
  "years_of_experience": "25",
  "current_position": "N/A",
  "current_company": "N/A",
  "current_company_domain": "N/A",
  "current_company_business": "N/A",
  "previous_company": "N/A",
  "work_authorization": "N/A",
  "clearance": "N/A",
  "address": "N/A",
  "disability": "N/A",
  "primary_skills": "N/A",
  "social_media_id": "N/A",
  "patents_info": "N/A",
  "previous_domain_worked_history": "N/A",
  "linkedin_url": "N/A",
  "education": "[{\"school_or_college\":\"Suffolk County Community College\",\"course_name\":\"A.A.S - Physical Therapist Assistant\",\"years\":\"N/A\"}]",
  "work_experience": "[{\"position\":\"PTA-Home Care\",\"years\":\"2022-\",\"company\":\"Visitry\",\"domain\":\"N/A\"},{\"position\":\"Rideshare Driver\",\"years\":\"2022\",\"company\":\"Self-Employed\",\"domain\":\"N/A\"},{\"position\":\"Functional Technician\",\"years\":\"2016-2020\",\"company\":\"Functional Evaluation Testing of Florida\",\"domain\":\"N/A\"},{\"position\":\"PTA - Skilled Nursing / Rehab. Facility\",\"years\":\"2015-2016\",\"company\":\"Total Healthcare Staffing\",\"domain\":\"N/A\"},{\"position\":\"PTA - Outpatient Facility\",\"years\":\"2015\",\"company\":\"Orlin and Cohen Orthopedic Associates\",\"domain\":\"N/A\"},{\"position\":\"PTA - Skilled Nursing / Rehab. Facility\",\"years\":\"2013-2015\",\"company\":\"Tender Touch Rehab Services\",\"domain\":\"N/A\"},{\"position\":\"PTA - Skilled Nursing / Rehab. Facility\",\"years\":\"2012-2013\",\"company\":\"Rehab Alternatives\",\"domain\":\"N/A\"},{\"position\":\"PTA - Outpatient Facility\",\"years\":\"1990-2011\",\"company\":\"CBC Center for Sports and Physical Therapy\",\"domain\":\"N/A\"}]",
  "interests": "'N/A'",
  "speaking_languages": "'Bilingual (Spanish)'",
  "skills": "'Well-organized', ' Detail Oriented', ' Excellent Communication Skills', ' Bilingual (Spanish)', ' Flexible in working with Pediatric', ' Adolescent', ' Adult', ' and Geriatric Patients'",
  "projects_list": "'N/A'",
  "achievements": "'N/A'",
  "extra_activities": "'N/A'",
  "certificates": "'Licensed Physical Therapist Assistant - NY and FL', ' Current Certification of Healthcare - CPR / AED / BLS'",
  "city": "Plant City",
  "state": "FL",
  "job_title": "N/A",
  "resume_html_tag": "undefined",
  "source": "extension"
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

  def add_details(self, details):

    self.set_font('Arial', 'B', 12)
    full_name = details['first_name'] + ' ' + details['last_name']
    entire_name = full_name.encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 8, entire_name, ln=True)

    self.set_font('Arial', '', 10)
    position = details['position'].encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 6,'Job_title :'+" "+ position, ln=True)

    location = details['location'].encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 6,"location :"+" "+location, ln=True)

    email_id = details['email_id'].encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 6,'Email :'+" "+ email_id, ln=True)

    mobile_number = details['mobile_number'].encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 6,"Mobile :"+" "+ mobile_number, ln=True)

    d_o_b = details['date_of_birth'].encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 6, "Date of Birth :" + " " + d_o_b, ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Summary', ln=True)
    self.set_font('Arial', '', 10)
    description = details['description'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, description)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Education', ln=True)
    self.set_font('Arial', '', 10)
    if type(details['education']) == str:
      education_list = eval(details['education'])
      for education in education_list:
        school_or_college = education['school_or_college'].encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 6, "School/College: " + school_or_college, ln=True)
        course_name = education['course_name'].encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 6, "Course Name: " + course_name, ln=True)
        years = education['years'].encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 6, "Years: " + years, ln=True)


    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Skills', ln=True)
    self.set_font('Arial', '', 10)
    if type(details['skills']) == str:
      skills_list = eval(details['skills'])
      for skills in skills_list:
        skills = skills.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 6, skills, ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Work Experience', ln=True)
    self.set_font('Arial', '', 10)
    if type(details['education']) == str:
      work_experience = eval(details['work_experience'])
      for experience in work_experience:
        self.set_font('Arial', 'BU', 10)
        position = experience['position'].encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 6, "Position: " + position, ln=True)
        self.set_font('Arial', '', 10)
        company = experience['company'].encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 6, "Company: " + company, ln=True)
        years = experience['years'].encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 6, "Years: " + years, ln=True)
        domain = experience['domain'].encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 6, "Domain: " + domain, ln=True)
        self.ln(3)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Interests', ln=True)
    self.set_font('Arial', '', 10)
    interests = details['interests'].replace("'",'').encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 6, interests, ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Speaking Languages', ln=True)
    self.set_font('Arial', '', 10)
    speaking_languages = details['speaking_languages'].replace("'",'').encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 6, speaking_languages, ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    certificates = details['certificates'].encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 10, 'Certificates', ln=True)
    self.set_font('Arial', '', 10)
    for certificate in details['certificates'].split(","):
      self.multi_cell(0, 6, certificate.replace("'",''))

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Achievements', ln=True)
    self.set_font('Arial', '', 10)
    for achievement in details['achievements'].split(","):
      achievement = achievement.replace("'",'').encode('latin-1', 'replace').decode('latin-1')
      self.multi_cell(0, 6, achievement.replace('’', ''))

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Projects List', ln=True)
    self.set_font('Arial', '', 10)
    for project in details['projects_list'].split(","):
      projects_list = project.replace("'",'').encode('latin-1', 'replace').decode('latin-1')
      self.multi_cell(0, 6, projects_list)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 6, 'Years Of Experience:', ln=True)
    self.set_font('Arial', '', 10)
    years_of_experience = details['years_of_experience'].encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 6, years_of_experience, ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Current_position:', ln=True)
    self.set_font('Arial', '', 10)
    current_position = details['current_position'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, current_position)

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Current_company:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    current_company = details['current_company'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, current_company)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Current_company_domain:', ln=True)
    self.set_font('Arial', '', 10)
    current_company_domain = details['current_company_domain'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, current_company_domain)

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Current_company_business:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    current_company_business = details['current_company_business'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, current_company_business)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Previous_company:', ln=True)
    self.set_font('Arial', '', 10)
    previous_company = details['previous_company'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, previous_company)

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Previous_domain_worked_history:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    previous_domain_worked_history = details['previous_domain_worked_history'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, previous_domain_worked_history)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Work_authorization:', ln=True)
    self.set_font('Arial', '', 10)
    work_authorization = details['work_authorization'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, work_authorization)

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Clearance:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    clearance = details['clearance'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, clearance)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Address', ln=True)
    self.set_font('Arial', '', 10)
    address = details['address'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 6, address)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Disability:', ln=True)
    self.set_font('Arial', '', 10)
    disability = details['disability'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, disability)

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Patents_info:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    patents_info = details['patents_info'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, patents_info)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Primary Skills', ln=True)
    self.set_font('Arial', '', 10)
    if type(details['primary_skills']) == str:
      for skills in details['primary_skills'].split(','):
        skills = skills.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 6, skills, ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'extra_activities', ln=True)
    self.set_font('Arial', '', 10)
    extra_activities = details['extra_activities'].replace("'",'').encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 6, extra_activities, ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Job_title', ln=True)
    self.set_font('Arial', '', 10)
    job_title = details['job_title'].encode('latin-1', 'replace').decode('latin-1')
    self.cell(0, 6, job_title, ln=True)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'city:', ln=True)
    self.set_font('Arial', '', 10)
    city = details['city'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, city)

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'state:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    state = details['state'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, state)

    self.ln(3)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'social_media_id:', ln=True)
    self.set_font('Arial', '', 10)
    social_media_id = details['social_media_id'].encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, social_media_id)

    self.set_y(self.get_y() - 14)
    self.set_x(self.w - 90)
    self.set_font('Arial', 'BU', 12)
    self.cell(0, 10, 'Linkedin_url:', ln=True)
    self.set_font('Arial', '', 10)
    self.set_y(self.get_y() - 0)
    self.set_x(self.w - 90)
    url = details['linkedin_url'].replace("'",'').encode('latin-1', 'replace').decode('latin-1')
    self.multi_cell(0, 5, url)


pdf = PDF()
pdf.add_page()
pdf.add_details(details)
pdf.output('resume.pdf')