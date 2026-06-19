#!/usr/bin/env python3
"""
NorthStar Regional Health Network — Synthetic Document Ecosystem Generator
For cybersecurity training use only. All data is 100% fictional.
"""

import os
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

BASE = Path("/tmp/northstar")

# ─── FICTIONAL DATA POOLS ────────────────────────────────────────────────────

FIRST_NAMES = [
    "Aaliyah","Adrian","Amara","Anastasia","Andre","Angelica","Beatriz","Bernard",
    "Brianna","Calvin","Camille","Carlos","Celeste","Chen","Clarence","Colette",
    "Damaris","Darnell","Dashiell","Delphine","Dmitri","Dominique","Elara","Elijah",
    "Esperanza","Evangeline","Fatima","Felix","Fernanda","Fletcher","Gabrielle","Grant",
    "Greta","Hector","Helena","Imani","Isaiah","Ivan","Jacinda","Jamison","Jasper",
    "Josephine","Kaden","Kameko","Kenji","Kwame","Laila","Langston","Larissa","Latasha",
    "Leandro","Leonora","Lila","Lionel","Lisette","Loretta","Luciana","Mabel","Malik",
    "Marcus","Margaux","Marisol","Mateo","Miriam","Nadia","Naomi","Nelson","Nikolai",
    "Nkechi","Octavia","Omar","Ophelia","Orlando","Paloma","Patricia","Quincy","Rafael",
    "Ramona","Reginald","Rosalind","Sasha","Selene","Simone","Solomon","Tanisha","Tobias",
]

LAST_NAMES = [
    "Abernathy","Adeyemi","Alvarado","Ashworth","Baxter","Beaumont","Beckford","Brennan",
    "Calloway","Castellano","Chambers","Christodoulou","Cisneros","Clarkson","Colburn",
    "Delaney","Delgado","Drummond","Dukakis","Eastwood","Ellington","Espinoza","Farrow",
    "Fitzgerald","Flores","Fontaine","Garland","Gideon","Goldstein","Guerrero","Harmon",
    "Hastings","Hawthorne","Hendricks","Holloway","Hubbard","Ingram","Ishibashi","Jacobson",
    "Kaminski","Kaufman","Kealoha","Kessler","Kimura","Kowalski","Landers","Lavoie",
    "Lawson","Leblanc","Lindqvist","Lozano","Macintyre","Maldonado","Matos","Mcallister",
    "Mccullough","Mendenhall","Merriweather","Miyamoto","Nakamura","Navarro","Okonkwo",
    "Osei","Pacheco","Papadopoulos","Patel","Pemberton","Quintero","Radford","Ramirez",
    "Reinholt","Renfroe","Sandoval","Santiago","Satterfield","Shahidi","Sloane","Stromberg",
    "Takahashi","Tanner","Theriault","Thornton","Vasquez","Villanueva","Wainwright","Whitmore",
]

PHYSICIANS = [
    "Dr. Adrienne Holloway","Dr. Bernard Nakamura","Dr. Celeste Okonkwo",
    "Dr. Damaris Patel","Dr. Elijah Fontaine","Dr. Fernanda Castillo",
    "Dr. Grant Lindqvist","Dr. Helena Merriweather","Dr. Ivan Kowalski",
    "Dr. Josephine Theriault","Dr. Kwame Asante","Dr. Larissa Beaumont",
    "Dr. Marcus Ishibashi","Dr. Nadia Villanueva","Dr. Omar Goldstein",
    "Dr. Patricia Drummond","Dr. Quincy Espinoza","Dr. Ramona Takahashi",
    "Dr. Solomon Delaney","Dr. Tanisha Wainwright","Dr. Tobias Chamberlain",
    "Dr. Valentina Reinholt","Dr. Winston Delgado","Dr. Xavier Mccullough",
    "Dr. Yara Sandoval","Dr. Zachary Pemberton","Dr. Amara Christodoulou",
    "Dr. Blaine Osei","Dr. Carmen Jacobson","Dr. Desmond Kaminski",
]

MANAGERS = [
    "Sandra Whitmore","Derek Calloway","Loretta Ingram","Marcus Ashworth",
    "Pauline Guerrero","Theodore Harmon","Vanessa Lozano","Bradford Kimura",
    "Claudette Matos","Eugene Fitzgerald","Harriet Clarkson","Jerome Garland",
    "Kathryn Maldonado","Lionel Chambers","Miriam Lavoie","Norman Ellington",
    "Odessa Vasquez","Percival Satterfield","Rowena Mendenhall","Stuart Kealoha",
]

INSURANCE_COMPANIES = [
    "BluePeak Health Partners","Meridian Coverage Group","TrueCore Benefits LLC",
    "Cascade Health Shield","Summit Medical Assurance","Pinnacle Care Network",
    "Horizon Wellness Group","Vanguard Health Solutions","Apex Benefit Partners",
    "Crestline Insurance Collective",
]

STREETS = [
    "Maple Ridge Drive","Hollow Creek Lane","Sunfield Terrace","Ironwood Court",
    "Bramblewood Avenue","Copperleaf Circle","Dunmore Street","Elmsgate Road",
    "Foxglove Way","Glenbrook Boulevard","Harvest Moon Drive","Ironbridge Pass",
    "Juniper Crest Road","Kestrel Hollow Lane","Larkspur Trail","Millstone Court",
    "Northgate Drive","Old Mill Road","Pinehaven Circle","Quarrystone Way",
]

CITIES = ["Westfield","Crestview","Hartmoor","Lakedale"]
STATE = "NV"

DEPARTMENTS = [
    "Nursing","Radiology","Emergency","Cardiology","Oncology","Pediatrics",
    "Orthopedics","Administration","Information Technology","Billing","Human Resources",
    "Housekeeping","Security","Laboratory","Pharmacy","Surgery","Psychiatry",
    "Physical Therapy","Compliance","Executive",
]

ROLES = [
    "Registered Nurse","Licensed Practical Nurse","Physician","Medical Assistant",
    "Administrative Coordinator","IT Specialist","Billing Specialist","Housekeeper",
    "Security Officer","Laboratory Technician","Pharmacist","Surgical Technician",
    "Compliance Officer","HR Generalist","Data Analyst","Radiology Technician",
    "Physical Therapist","Patient Services Representative","Network Administrator",
    "Executive Assistant",
]

DIAGNOSES = [
    ("Z00.00","Encounter for general adult medical examination"),
    ("I10","Essential hypertension"),
    ("E11.9","Type 2 diabetes mellitus without complications"),
    ("J06.9","Acute upper respiratory infection, unspecified"),
    ("M54.5","Low back pain"),
    ("K21.0","Gastroesophageal reflux disease with esophagitis"),
    ("F32.1","Major depressive disorder, single episode, moderate"),
    ("J45.20","Mild intermittent asthma, uncomplicated"),
    ("E78.5","Hyperlipidemia, unspecified"),
    ("N39.0","Urinary tract infection, site not specified"),
    ("G43.909","Migraine, unspecified, not intractable"),
    ("M17.11","Primary osteoarthritis, right knee"),
    ("Z23","Encounter for immunization"),
    ("R05","Cough"),
    ("R51","Headache"),
]

CPT_CODES = [
    ("99213","Office visit, established patient, low complexity"),
    ("99214","Office visit, established patient, moderate complexity"),
    ("99215","Office visit, established patient, high complexity"),
    ("99203","Office visit, new patient, low complexity"),
    ("93000","Electrocardiogram, routine, with interpretation"),
    ("85025","Complete blood count with differential"),
    ("80053","Comprehensive metabolic panel"),
    ("71046","Chest X-ray, 2 views"),
    ("70553","MRI brain with and without contrast"),
    ("74177","CT abdomen and pelvis with contrast"),
    ("99232","Subsequent hospital care, moderate complexity"),
    ("99283","Emergency department visit, moderate severity"),
    ("90837","Psychotherapy, 60 minutes"),
    ("97110","Therapeutic exercises"),
    ("36415","Routine venipuncture"),
]

MEDICATIONS = [
    "Lisinopril 10mg daily","Metformin 500mg twice daily","Atorvastatin 40mg at bedtime",
    "Omeprazole 20mg daily","Sertraline 50mg daily","Albuterol inhaler PRN",
    "Amlodipine 5mg daily","Levothyroxine 50mcg daily","Metoprolol succinate 25mg daily",
    "Gabapentin 300mg three times daily","Hydrochlorothiazide 25mg daily",
    "Prednisone 20mg taper","Amoxicillin 500mg three times daily x10 days",
    "Ibuprofen 400mg as needed","Fluticasone nasal spray daily",
]

LAB_TESTS = [
    ("WBC","4.5-11.0 K/uL"),("RBC","4.2-5.8 M/uL"),("Hemoglobin","12.0-17.5 g/dL"),
    ("Hematocrit","36-52%"),("Platelets","150-400 K/uL"),("Sodium","136-145 mEq/L"),
    ("Potassium","3.5-5.1 mEq/L"),("Creatinine","0.6-1.2 mg/dL"),
    ("Glucose","70-100 mg/dL"),("HbA1c","<5.7%"),("Total Cholesterol","<200 mg/dL"),
    ("LDL","<100 mg/dL"),("HDL",">40 mg/dL"),("Triglycerides","<150 mg/dL"),
    ("TSH","0.4-4.0 mIU/L"),
]

VENDORS = [
    "Apex Medical Supplies Co.","BioShield Protective Equipment Inc.",
    "CoreLogic Healthcare IT","DataVault Backup Solutions LLC",
    "EverGreen Facilities Management","FrontLine Security Services",
    "GlobalMed Pharmaceuticals Distribution","HealthStream Training Partners",
    "IntelliScan Imaging Technologies","JustCare Staffing Agency",
    "Kronos Workforce Management","Linkserv Network Solutions",
    "MedEquip Rental Corp","NovaTech Systems","OmniCare Consulting Group",
]

EHR_SYSTEMS = {
    2016: "MedTrack v1",
    2017: "MedTrack v1",
    2018: "MedTrack v2",
    2019: "MedTrack v2",
    2020: "MedTrack v2",
    2021: "MedTrack v3",
    2022: "MedTrack v3",
    2023: "NovaMed EHR",
    2024: "NovaMed EHR",
    2025: "NovaMed EHR",
    2026: "NovaMed EHR",
}

ORG_NAME = {
    2016: "Westfield General Hospital Network",
    2017: "Westfield General Hospital Network",
    2018: "Westfield General Hospital Network",
    2019: "NorthStar Regional Health Network",
    2020: "NorthStar Regional Health Network",
    2021: "NorthStar Regional Health Network",
    2022: "NorthStar Regional Health Network",
    2023: "NorthStar Regional Health Network",
    2024: "NorthStar Regional Health Network",
    2025: "NorthStar Regional Health Network",
    2026: "NorthStar Regional Health Network",
}

# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

def rname():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def remail(name):
    parts = name.lower().split()
    domains = ["northstar-health.internal","northstarhealth.local","corp.northstar-health.test"]
    return f"{parts[0]}.{parts[-1]}@{random.choice(domains)}"

def rssn():
    return f"9{random.randint(0,9)}{random.randint(0,9)}-{random.randint(10,99)}-{random.randint(1000,9999)}"

def rphone():
    return f"(555) {random.randint(200,999)}-{random.randint(1000,9999)}"

def raddress():
    num = random.randint(100, 9999)
    street = random.choice(STREETS)
    city = random.choice(CITIES)
    return f"{num} {street}, {city}, {STATE} {random.randint(89000,89999)}"

def rdate(start_year=2016, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(min(end_year, 2026), 6, 15)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

def rdob():
    age = random.randint(0, 95)
    base = datetime(2026, 6, 15)
    return base - timedelta(days=age*365 + random.randint(0,364))

def rempid():
    return f"EMP-{random.randint(10000,99999)}"

def rmrn():
    return f"MRN-{random.randint(10000000,99999999)}"

def rserial():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789"
    return "".join(random.choices(chars, k=10))

def rmac():
    return ":".join(f"{random.randint(0,255):02X}" for _ in range(6))

def rsalary(role):
    ranges = {
        "Physician": (180000, 320000),
        "Pharmacist": (110000, 145000),
        "Registered Nurse": (62000, 95000),
        "Licensed Practical Nurse": (45000, 62000),
        "Physical Therapist": (72000, 98000),
        "Radiology Technician": (58000, 82000),
        "Laboratory Technician": (48000, 68000),
        "Surgical Technician": (52000, 72000),
        "IT Specialist": (65000, 105000),
        "Network Administrator": (72000, 115000),
        "Compliance Officer": (68000, 95000),
        "HR Generalist": (52000, 72000),
        "Billing Specialist": (42000, 58000),
        "Administrative Coordinator": (40000, 56000),
        "Executive Assistant": (48000, 68000),
        "Data Analyst": (62000, 88000),
        "Medical Assistant": (35000, 48000),
        "Housekeeper": (30000, 40000),
        "Security Officer": (35000, 52000),
        "Patient Services Representative": (36000, 50000),
    }
    lo, hi = ranges.get(role, (38000, 72000))
    return random.randint(lo // 1000, hi // 1000) * 1000

def get_org(year):
    return ORG_NAME.get(year, "NorthStar Regional Health Network")

def get_ehr(year):
    return EHR_SYSTEMS.get(year, "NovaMed EHR")

def maybe_typo(text, rate=0.02):
    if random.random() < rate:
        words = text.split()
        if words:
            idx = random.randint(0, len(words)-1)
            w = words[idx]
            if len(w) > 3:
                i = random.randint(1, len(w)-2)
                w = w[:i] + w[i+1:]
                words[idx] = w
        return " ".join(words)
    return text

def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

counter = [0]
total_target = 3000

def tick(label=""):
    counter[0] += 1
    if counter[0] % 100 == 0:
        print(f"Generated {counter[0]}/{total_target} documents... [{label}]")

# ─── FOLDER STRUCTURE ────────────────────────────────────────────────────────

FOLDERS = []
for yr in range(2016, 2027):
    FOLDERS.append(f"HR/Payroll/{yr}")
    FOLDERS.append(f"Patients/{yr}")
    FOLDERS.append(f"Billing/{yr}")

FOLDERS += [
    "HR/Personnel/Active","HR/Personnel/Terminated","HR/Personnel/Archive",
    "HR/Benefits/Enrollment","HR/Benefits/Archive",
    "HR/Training","HR/Disciplinary","HR/Onboarding","HR/Offboarding",
    "Patients/Active","Patients/Archived",
    "Insurance/Verification","Insurance/Claims",
    "IT/Tickets/Open","IT/Tickets/Closed",
    "IT/Assets/Endpoints","IT/Assets/Servers",
    "IT/Security/Incidents","IT/Security/Vulnerability",
    "IT/ChangeManagement",
    "Executive/BoardMeetings","Executive/Budget","Executive/Strategy",
    "Compliance/HIPAA","Compliance/Audits",
    "Legal/Contracts","Legal/Vendor",
    "Archive/Old_HR","Archive/Payroll2017",
    "Shared/Old","Desktop","Downloads","Temp",
    "DoNotDelete","Stuff","Random",
]

for f in FOLDERS:
    (BASE / f).mkdir(parents=True, exist_ok=True)

# ─── HR DOCUMENT GENERATORS ──────────────────────────────────────────────────

def gen_employment_application():
    name = rname()
    role = random.choice(ROLES)
    dt = rdate(2016, 2026)
    yr = dt.year
    org = get_org(yr)
    dob = rdob()
    addr = raddress()
    phone = rphone()
    email = remail(name)
    ssn = rssn()
    prev_employer = random.choice(["Hartmoor Medical Center","Lakedale Community Hospital",
        "Crestview Urgent Care","Desert Valley Clinic","Summit Health Partners",
        "Ridgeline Family Medicine","Valley General Hospital"])
    content = f"""{org}
EMPLOYMENT APPLICATION
Date: {dt.strftime('%B %d, %Y')}

PERSONAL INFORMATION
Full Name: {name}
Date of Birth: {dob.strftime('%m/%d/%Y')}
Social Security Number: {ssn}
Address: {addr}
Phone: {phone}
Email: {email}

POSITION APPLIED FOR
Position: {role}
Department: {random.choice(DEPARTMENTS)}
Employment Type: {random.choice(['Full-Time','Part-Time','PRN'])}
Desired Start Date: {(dt + timedelta(days=random.randint(14,45))).strftime('%m/%d/%Y')}
Desired Salary: ${rsalary(role):,}

EDUCATION
Highest Degree: {random.choice(['Associate of Science','Bachelor of Science','Master of Science','Doctor of Medicine','High School Diploma'])}
Institution: {random.choice(['Westfield Community College','Crestview University','Hartmoor State University','Lakedale College of Health Sciences'])}
Year Graduated: {random.randint(1995, 2023)}

PREVIOUS EMPLOYMENT
Most Recent Employer: {prev_employer}
Position Held: {random.choice(ROLES)}
Dates of Employment: {random.randint(2010,min(2020,dt.year-1))} - {min(dt.year, 2024)}
Reason for Leaving: {random.choice(['Career advancement','Relocation','Company downsizing','Seeking new opportunities','Contract ended'])}

REFERENCES
{rname()} — {rphone()}
{rname()} — {rphone()}

CERTIFICATIONS
{random.choice(['BLS Certified','ACLS Certified','CNA','RN License NV-XXXXXX','None listed'])}

I certify that all information provided is accurate and complete.
Signature: {name}     Date: {dt.strftime('%m/%d/%Y')}
"""
    return maybe_typo(content)


def gen_offer_letter():
    name = rname()
    role = random.choice(ROLES)
    dt = rdate(2016, 2026)
    yr = dt.year
    org = get_org(yr)
    salary = rsalary(role)
    manager = random.choice(MANAGERS)
    start = dt + timedelta(days=random.randint(14,30))
    content = f"""{org}
Office of Human Resources
{raddress()}

{dt.strftime('%B %d, %Y')}

{name}
{raddress()}

Dear {name.split()[0]},

We are pleased to extend an offer of employment for the position of {role} within the {random.choice(DEPARTMENTS)} Department at {org}.

OFFER DETAILS
Position: {role}
Department: {random.choice(DEPARTMENTS)}
Start Date: {start.strftime('%B %d, %Y')}
Employment Status: {random.choice(['Full-Time Regular','Part-Time Regular','PRN/As Needed'])}
Annual Salary: ${salary:,} (paid {random.choice(['bi-weekly','semi-monthly'])})
Reporting To: {manager}

BENEFITS PACKAGE
- Medical Insurance: {random.choice(INSURANCE_COMPANIES)} ({random.choice(['PPO','HMO','HDHP'])} plan)
- Dental and Vision coverage
- 401(k) with {random.randint(3,6)}% employer match (vesting after {random.choice(['1 year','2 years','3 years'])})
- Paid Time Off: {random.randint(10,20)} days per year accrual
- {random.randint(6,11)} Paid Holidays annually
- Employee Assistance Program
- Tuition Reimbursement up to ${random.randint(3000,6000):,}/year

CONTINGENCIES
This offer is contingent upon:
1. Successful completion of a background check
2. Drug screening (negative result required)
3. Verification of credentials and licensure
4. Completion of pre-employment health screening

Please sign and return this letter by {(dt + timedelta(days=7)).strftime('%B %d, %Y')}.

Sincerely,
{random.choice(MANAGERS)}
Director of Human Resources
{org}

ACCEPTANCE: I accept the above offer of employment.
Signature: ___________________________  Date: ___________
"""
    return content


def gen_employee_record():
    name = rname()
    role = random.choice(ROLES)
    dept = random.choice(DEPARTMENTS)
    hire_date = rdate(2016, 2025)
    yr = hire_date.year
    org = get_org(yr)
    emp_id = rempid()
    salary = rsalary(role)
    manager = random.choice(MANAGERS)
    status = random.choices(["Active","Active","Active","Terminated","On Leave"],weights=[6,6,6,1,1])[0]
    content = f"""{org}
EMPLOYEE RECORD — CONFIDENTIAL
Generated: {datetime.now().strftime('%Y-%m-%d')}

EMPLOYEE INFORMATION
Employee ID: {emp_id}
Full Name: {name}
SSN: {rssn()}
Date of Birth: {rdob().strftime('%m/%d/%Y')}
Gender: {random.choice(['Male','Female','Non-binary','Prefer not to disclose'])}
Address: {raddress()}
Phone (Primary): {rphone()}
Phone (Mobile): {rphone()}
Email (Work): {remail(name)}
Emergency Contact: {rname()} — {rphone()} — {random.choice(['Spouse','Parent','Sibling','Partner','Friend'])}

EMPLOYMENT DETAILS
Position: {role}
Department: {dept}
Employment Status: {status}
Employment Type: {random.choice(['Full-Time','Part-Time'])}
Hire Date: {hire_date.strftime('%m/%d/%Y')}
Badge Number: {random.randint(1000,9999)}
Manager: {manager}
Cost Center: CC-{random.randint(1000,9999)}

COMPENSATION
Current Salary: ${salary:,}/year
Pay Grade: {random.choice(['G1','G2','G3','G4','G5','M1','M2','E1'])}
Last Review Date: {rdate(yr, 2026).strftime('%m/%d/%Y')}
Last Increase: {random.randint(2,8)}%

INSURANCE & BENEFITS
Health Plan: {random.choice(INSURANCE_COMPANIES)}
Plan Type: {random.choice(['PPO','HMO','HDHP'])}
Dental: {random.choice(['Enrolled','Waived'])}
Vision: {random.choice(['Enrolled','Waived'])}
401(k) Contribution: {random.randint(2,15)}%

NOTES
EHR System Access: {get_ehr(yr)}
Parking Permit: {random.choice(['Lot A','Lot B','Lot C','Garage Level 2','None'])}
"""
    return maybe_typo(content)


def gen_performance_review():
    name = rname()
    role = random.choice(ROLES)
    manager = random.choice(MANAGERS)
    dt = rdate(2016, 2026)
    yr = dt.year
    org = get_org(yr)
    overall = random.randint(1, 5)
    ratings = {
        "Quality of Work": random.randint(1,5),
        "Attendance & Punctuality": random.randint(1,5),
        "Communication Skills": random.randint(1,5),
        "Teamwork & Collaboration": random.randint(1,5),
        "Patient/Customer Service": random.randint(1,5),
        "Adherence to Policy": random.randint(1,5),
        "Initiative & Problem Solving": random.randint(1,5),
    }
    comments = [
        f"{name.split()[0]} has demonstrated {random.choice(['consistent','improving','exceptional','adequate','below-average'])} performance throughout the review period.",
        f"Areas of strength include {random.choice(['clinical documentation','team communication','patient interactions','technical skills','scheduling adherence'])}.",
        f"Opportunities for growth: {random.choice(['time management','documentation accuracy','interdepartmental communication','policy compliance','initiative on projects'])}.",
        f"Goals for next period: {random.choice(['Complete ACLS recertification','Reduce documentation errors by 15%','Mentor one new team member','Complete EHR advanced training','Lead one department meeting per quarter'])}.",
    ]
    rating_block = "\n".join(f"  {k}: {v}/5" for k, v in ratings.items())
    content = f"""{org}
ANNUAL PERFORMANCE REVIEW
Review Period: {yr-1} — {yr}
Date: {dt.strftime('%B %d, %Y')}

EMPLOYEE: {name}
Position: {role}
Department: {random.choice(DEPARTMENTS)}
Reviewing Manager: {manager}

PERFORMANCE RATINGS (1=Unsatisfactory, 3=Meets Expectations, 5=Exceeds Expectations)
{rating_block}
Overall Rating: {overall}/5

MANAGER COMMENTS
{chr(10).join(comments)}

EMPLOYEE SELF-ASSESSMENT
{name.split()[0]} noted: "{random.choice([
    'I feel I have grown significantly this year and am proud of my contributions.',
    'I would like more opportunities for professional development.',
    'I believe my documentation has improved but I still have room to grow.',
    'This has been a challenging year but I am committed to improvement.',
    'I am proud of how our team handled the increased patient volume.'
])}"

GOALS ESTABLISHED
1. {random.choice(['Complete mandatory training modules by Q2','Improve patient satisfaction scores','Reduce overtime utilization','Attend at least one conference','Cross-train in adjacent department'])}
2. {random.choice(['Mentor new hire during onboarding','Lead process improvement initiative','Obtain additional certification','Improve EHR utilization metrics','Reduce documentation turnaround time'])}

Manager Signature: {manager}    Date: {dt.strftime('%m/%d/%Y')}
Employee Signature: {name}      Date: {dt.strftime('%m/%d/%Y')}
"""
    return maybe_typo(content)


def gen_payroll_report():
    dt = rdate(2016, 2026)
    yr = dt.year
    org = get_org(yr)
    dept = random.choice(DEPARTMENTS)
    num_emp = random.randint(8, 35)
    employees = [(rname(), random.choice(ROLES), rsalary(random.choice(ROLES))) for _ in range(num_emp)]
    period_start = dt - timedelta(days=14)
    gross = sum(e[2] for e in employees) // 26
    content = f"""{org}
PAYROLL REPORT — {dept.upper()} DEPARTMENT
Pay Period: {period_start.strftime('%m/%d/%Y')} — {dt.strftime('%m/%d/%Y')}
Generated: {dt.strftime('%m/%d/%Y')}
Prepared by: {random.choice(MANAGERS)} (Payroll)

DEPARTMENT SUMMARY
Department: {dept}
Number of Employees: {num_emp}
Pay Period Gross: ${gross:,}
Total YTD Gross: ${gross * random.randint(2,24):,}

EMPLOYEE BREAKDOWN
{'Name':<30} {'Role':<35} {'Gross Pay':>12}
{'-'*80}
"""
    for emp_name, emp_role, emp_sal in employees:
        biweekly = emp_sal // 26
        content += f"{emp_name:<30} {emp_role:<35} ${biweekly:>10,}\n"
    content += f"""
{'-'*80}
DEPARTMENT TOTAL: ${gross:,}

DEDUCTIONS SUMMARY
  Federal Withholding: ${int(gross*0.22):,}
  State Withholding: ${int(gross*0.05):,}
  FICA (Social Security): ${int(gross*0.062):,}
  Medicare: ${int(gross*0.0145):,}
  Health Insurance: ${random.randint(2000,8000):,}
  Dental/Vision: ${random.randint(300,900):,}
  401(k) Employee: ${int(gross*random.uniform(0.03,0.10)):,}
  Garnishments: ${random.randint(0,500):,}

NET PAY: ${int(gross*0.68):,}

Authorized by: {random.choice(MANAGERS)}
"""
    return content


def gen_pto_request():
    name = rname()
    dt = rdate(2018, 2026)
    days = random.randint(1, 10)
    status = random.choice(["APPROVED","DENIED","PENDING"])
    content = f"""NorthStar Regional Health Network
PTO / LEAVE REQUEST FORM
Submitted: {dt.strftime('%m/%d/%Y')}

Employee: {name}
Department: {random.choice(DEPARTMENTS)}
Position: {random.choice(ROLES)}
Employee ID: {rempid()}

Leave Type: {random.choice(['Vacation','Personal','Sick','Bereavement','FMLA','Jury Duty'])}
Start Date: {(dt + timedelta(days=random.randint(7,60))).strftime('%m/%d/%Y')}
Return Date: {(dt + timedelta(days=random.randint(8,70))).strftime('%m/%d/%Y')}
Days Requested: {days}
PTO Balance Prior to Request: {random.randint(days, 30)} days

Reason: {random.choice(['Family vacation','Personal appointment','Medical procedure recovery',
    'Family event out of state','Mental health day','Scheduled surgery','Child care needs','Bereavement'])}

Coverage Arrangements: {random.choice(['Covered by','Shifts covered by'])} {rname()}

STATUS: {status}
{f"Denied Reason: {random.choice(['Insufficient PTO balance','Staffing requirements','Blackout period'])}" if status == 'DENIED' else ''}

Manager Approval: {random.choice(MANAGERS)}
Date: {(dt + timedelta(days=random.randint(1,3))).strftime('%m/%d/%Y')}
"""
    return content


def gen_disciplinary_notice():
    name = rname()
    dt = rdate(2017, 2026)
    manager = random.choice(MANAGERS)
    org = get_org(dt.year)
    violations = [
        ("Tardiness","Employee arrived late on multiple occasions without prior notification.",
         "Employee is expected to arrive on time per scheduled shift. Further occurrences may result in suspension."),
        ("Policy Violation","Employee was observed using a personal mobile device in a restricted patient care area.",
         "Employee must adhere to the No Personal Device Policy in all patient care zones."),
        ("Insubordination","Employee refused a direct instruction from supervisor without reasonable cause.",
         "All reasonable instructions from supervisors must be followed. Employee is reminded of chain of command."),
        ("Documentation Failure","Employee failed to complete required patient documentation within the mandated timeframe.",
         "All patient documentation must be completed within 4 hours of encounter per departmental policy."),
        ("Dress Code Violation","Employee did not comply with the organization's uniform and appearance standards.",
         "Employee is required to report to work in full compliance with the uniform policy."),
    ]
    vtype, vdesc, vaction = random.choice(violations)
    level = random.choice(["Verbal Warning (Documented)","Written Warning","Final Written Warning"])
    content = f"""{org}
DISCIPLINARY NOTICE — CONFIDENTIAL
Date: {dt.strftime('%B %d, %Y')}

EMPLOYEE INFORMATION
Name: {name}
Employee ID: {rempid()}
Department: {random.choice(DEPARTMENTS)}
Position: {random.choice(ROLES)}
Manager: {manager}

NOTICE TYPE: {level}

VIOLATION CATEGORY: {vtype}

DESCRIPTION OF INCIDENT
Date(s) of Incident: {(dt - timedelta(days=random.randint(1,7))).strftime('%m/%d/%Y')}
{vdesc}

CORRECTIVE ACTION REQUIRED
{vaction}

CONSEQUENCE OF FURTHER VIOLATIONS
Failure to correct the above behavior may result in further disciplinary action up to and including termination of employment.

EMPLOYEE RESPONSE
{random.choice([
    'Employee acknowledged receipt and understanding of this notice.',
    'Employee disputed the characterization of events. Details documented separately.',
    'Employee accepted responsibility and committed to improvement.',
    'Employee declined to sign this notice but was given a copy.',
])}

Manager Signature: {manager}        Date: {dt.strftime('%m/%d/%Y')}
Employee Signature: {name}          Date: {dt.strftime('%m/%d/%Y')}
HR Witness: {random.choice(MANAGERS)}    Date: {dt.strftime('%m/%d/%Y')}
"""
    return maybe_typo(content)


def gen_benefits_enrollment():
    name = rname()
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    insurer = random.choice(INSURANCE_COMPANIES)
    content = f"""{org}
BENEFITS ENROLLMENT FORM
Open Enrollment Period: {dt.year} Annual Enrollment
Form Submitted: {dt.strftime('%m/%d/%Y')}

EMPLOYEE INFORMATION
Name: {name}
Employee ID: {rempid()}
SSN: {rssn()}
Date of Birth: {rdob().strftime('%m/%d/%Y')}
Department: {random.choice(DEPARTMENTS)}
Hire Date: {rdate(2010, dt.year).strftime('%m/%d/%Y')}

MEDICAL INSURANCE
Selected Plan: {insurer}
Plan Type: {random.choice(['PPO Gold','PPO Silver','HMO Standard','HDHP + HSA'])}
Coverage Level: {random.choice(['Employee Only','Employee + Spouse','Employee + Children','Family'])}
Employee Monthly Premium: ${random.randint(85,420):,}

DENTAL INSURANCE
{random.choice(['Enrolled — Premier Dental Plan ($18.50/month)','Waived — covered under spouse plan','Enrolled — Basic Dental Plan ($9.00/month)'])}

VISION INSURANCE
{random.choice(['Enrolled — EyeCare Plus ($6.20/month)','Waived'])}

401(k) RETIREMENT
Contribution Rate: {random.randint(2,15)}% of gross pay
Employer Match: {random.randint(3,6)}% (vested after {random.choice(['1','2','3'])} year(s))
Investment Election: {random.choice(['Target Date 2040 Fund','Balanced Growth Fund','Conservative Income Fund','Aggressive Growth Fund'])}

FLEXIBLE SPENDING ACCOUNT
FSA Election: ${random.randint(0,2750):,}/year
Dependent Care FSA: ${random.randint(0,5000):,}/year

LIFE INSURANCE
Basic Life (1x salary): Automatically enrolled
Supplemental Life: {random.choice(['1x salary','2x salary','3x salary','Declined'])}

Beneficiary (Primary): {rname()} — {random.choice(['Spouse','Child','Parent','Domestic Partner'])}
Beneficiary (Secondary): {rname()} — {random.choice(['Child','Sibling','Parent'])}

I certify the information above is accurate.
Signature: {name}    Date: {dt.strftime('%m/%d/%Y')}
"""
    return content


def gen_training_record():
    name = rname()
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    trainings = [
        ("HIPAA Privacy & Security Training", random.randint(60,90)),
        ("Annual Mandatory Safety Training", random.randint(45,60)),
        ("Fire Safety & Evacuation Procedures", 30),
        ("Bloodborne Pathogen Exposure Control", 45),
        ("Workplace Violence Prevention", 30),
        ("Patient Rights & Responsibilities", 45),
        ("Hand Hygiene Competency", 20),
        ("EHR System Training — " + get_ehr(dt.year), random.randint(60,180)),
    ]
    completed = random.sample(trainings, random.randint(3, len(trainings)))
    training_block = "\n".join(f"  [{random.choice(['PASS','PASS','PASS','FAIL'])}] {t[0]} — {t[1]} min — {rdate(dt.year, dt.year+1).strftime('%m/%d/%Y')}" for t in completed)
    content = f"""{org}
EMPLOYEE TRAINING COMPLETION RECORD
Year: {dt.year}
Generated: {dt.strftime('%m/%d/%Y')}

Employee: {name}
Employee ID: {rempid()}
Department: {random.choice(DEPARTMENTS)}
Position: {random.choice(ROLES)}

COMPLETED TRAINING MODULES
{training_block}

Compliance Status: {random.choice(['COMPLIANT','COMPLIANT','COMPLIANT','NON-COMPLIANT — FOLLOW UP REQUIRED'])}
Next Annual Due Date: {datetime(dt.year+1, dt.month, dt.day).strftime('%m/%d/%Y')}

Recorded by: {random.choice(MANAGERS)}
Learning Management System: {random.choice(['HealthStream LMS','NorthStar Learning Portal','Cornerstone OnDemand'])}
"""
    return content


def gen_exit_interview():
    name = rname()
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    reasons = [
        "Accepted position with higher compensation",
        "Relocating out of state",
        "Family responsibilities requiring reduced schedule",
        "Returning to school full-time",
        "Career change to a different field",
        "Dissatisfied with management style",
        "Limited advancement opportunities",
        "Work-life balance concerns",
        "Retirement",
    ]
    content = f"""{org}
EXIT INTERVIEW FORM
Date: {dt.strftime('%B %d, %Y')}

Employee: {name}
Employee ID: {rempid()}
Department: {random.choice(DEPARTMENTS)}
Position: {random.choice(ROLES)}
Last Day of Employment: {dt.strftime('%m/%d/%Y')}
Length of Employment: {random.randint(1,15)} year(s) {random.randint(0,11)} month(s)
Manager: {random.choice(MANAGERS)}

PRIMARY REASON FOR LEAVING
{random.choice(reasons)}

SURVEY RESPONSES (1=Strongly Disagree, 5=Strongly Agree)
My work was meaningful and rewarding: {random.randint(1,5)}
I had the tools and resources to do my job well: {random.randint(1,5)}
My manager supported my professional development: {random.randint(1,5)}
I felt my contributions were recognized: {random.randint(1,5)}
I would recommend {org} as an employer: {random.randint(1,5)}
The benefits package met my needs: {random.randint(1,5)}

OPEN FEEDBACK
What did you enjoy most? {random.choice([
    'The team culture and supportive colleagues.',
    'The patient interactions — very fulfilling work.',
    'The variety of cases and learning opportunities.',
    'Flexible scheduling options.',
    'Strong training and onboarding program.',
])}

What could be improved? {random.choice([
    'Staffing levels during peak hours need attention.',
    'More consistent communication from leadership.',
    'Better equipment and updated technology.',
    'More competitive compensation and benefits.',
    'Clearer advancement pathways.',
])}

Would you be eligible for rehire? {random.choice(['Yes','No','Yes — with conditions'])}

HR Interviewer: {random.choice(MANAGERS)}
"""
    return content


def gen_nw4_form():
    name = rname()
    dt = rdate(2016, 2026)
    content = f"""NorthStar Regional Health Network
EMPLOYEE WITHHOLDING FORM (NW-4)
For use in calculating payroll tax withholding — Fictional Training Document Only
Tax Year: {dt.year}

Step 1: Personal Information
Name: {name}
SSN: {rssn()}
Address: {raddress()}
Filing Status: {random.choice(['Single or Married Filing Separately','Married Filing Jointly','Head of Household'])}

Step 2: Multiple Jobs / Spouse Works
{random.choice(['Check here if applicable: [ ]','Completed worksheet on back','Not applicable'])}

Step 3: Claim Dependents
Number of qualifying children under 17: {random.randint(0,4)}
Number of other dependents: {random.randint(0,2)}
Total credits: ${random.randint(0,4)*2000 + random.randint(0,2)*500:,}

Step 4: Other Adjustments
Other income (not from jobs): ${random.randint(0,5000):,}
Additional withholding per pay period: ${random.randint(0,200)}

Step 5: Signature
I certify this certificate is correct.
Signature: {name}    Date: {dt.strftime('%m/%d/%Y')}

For Payroll Use:
Entered by: {random.choice(MANAGERS)}
Effective Pay Period: {dt.strftime('%m/%Y')}
"""
    return content


def gen_onboarding_packet():
    name = rname()
    role = random.choice(ROLES)
    dept = random.choice(DEPARTMENTS)
    start = rdate(2016, 2026)
    org = get_org(start.year)
    emp_id = rempid()
    content = f"""{org}
NEW EMPLOYEE ONBOARDING PACKET
Welcome, {name}!
Start Date: {start.strftime('%B %d, %Y')}
Employee ID: {emp_id}
Position: {role}
Department: {dept}

ONBOARDING CHECKLIST
[ ] Badge photo taken — Security Office, Room 104
[ ] Parking permit issued — Lot: {random.choice(['A','B','C'])} — Permit #: {random.randint(1000,9999)}
[ ] EHR Access Provisioned — System: {get_ehr(start.year)} — Username: {remail(name)}
[ ] VPN Access Request submitted — Ticket #: INC-{random.randint(10000,99999)}
[ ] HIPAA Training completed (mandatory Day 1)
[ ] ID Badge activated
[ ] Payroll Direct Deposit form submitted
[ ] NW-4 Withholding form submitted
[ ] Benefits enrollment packet received
[ ] Emergency Contact form submitted
[ ] Employee Handbook acknowledged
[ ] Department tour completed with: {random.choice(MANAGERS)}
[ ] IT equipment issued — {random.choice(['Laptop','Desktop'])} S/N: {rserial()}

ORIENTATION SCHEDULE
Day 1: HR Orientation — Building A, Conference Room 2B — 8:00 AM
Day 2: Department Shadow with {random.choice(MANAGERS)}
Day 3: EHR System Training — IT Training Lab
Day 4-5: Department-specific skills orientation

IT CREDENTIALS
Network Username: {remail(name)}
Temporary Password: {random.choice(['Welcome2024!','TempPass#1','OnBoard!23','NorthStar@1'])}
(Change required at first login)

IMPORTANT CONTACTS
IT Help Desk: (555) 400-HELP
HR Department: (555) 400-0100
Facilities: (555) 400-0200
Security: (555) 400-0300

Welcome to {org}. We are glad you're here.
HR Coordinator: {random.choice(MANAGERS)}
"""
    return content


# ─── GENERATE HR DOCUMENTS ───────────────────────────────────────────────────

def generate_hr_documents():
    generated = 0

    # Employment Applications
    for i in range(60):
        dt = rdate(2016, 2026)
        subdir = "HR/Onboarding" if random.random() > 0.5 else f"HR/Personnel/{'Active' if random.random()>0.3 else 'Terminated'}"
        fname = f"employment_application_{rname().replace(' ','_')}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / subdir / fname, gen_employment_application())
        tick("HR-App"); generated += 1

    # Offer Letters
    for i in range(50):
        dt = rdate(2016, 2026)
        fname = f"offer_letter_{rname().replace(' ','_')}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / "HR/Personnel/Active" / fname, gen_offer_letter())
        tick("HR-Offer"); generated += 1

    # Employee Records
    names_pool = [rname() for _ in range(80)]
    for i, name in enumerate(names_pool):
        status = random.choices(["Active","Terminated","Archive"],weights=[7,2,1])[0]
        subdir = f"HR/Personnel/{'Active' if status=='Active' else 'Terminated' if status=='Terminated' else 'Archive'}"
        emp_id = rempid()
        fname = f"employee_record_{emp_id}_{name.replace(' ','_')}.txt"
        write_file(BASE / subdir / fname, gen_employee_record())
        tick("HR-Rec"); generated += 1

    # Performance Reviews
    for i in range(80):
        dt = rdate(2016, 2026)
        name = rname().replace(' ','_')
        fname = f"perf_review_{name}_{dt.year}.txt"
        write_file(BASE / "HR/Personnel/Active" / fname, gen_performance_review())
        tick("HR-Perf"); generated += 1

    # Payroll Reports
    for yr in range(2016, 2027):
        for month in range(1, 13, 2):
            if yr == 2026 and month > 6:
                break
            fname = f"payroll_report_{yr}_{month:02d}.txt"
            write_file(BASE / f"HR/Payroll/{yr}" / fname, gen_payroll_report())
            tick("HR-Pay"); generated += 1

    # PTO Requests
    for i in range(70):
        dt = rdate(2017, 2026)
        fname = f"pto_request_{rname().replace(' ','_')}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / "HR/Personnel/Active" / fname, gen_pto_request())
        tick("HR-PTO"); generated += 1

    # Disciplinary Notices
    for i in range(40):
        dt = rdate(2017, 2026)
        fname = f"disciplinary_{rname().replace(' ','_')}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / "HR/Disciplinary" / fname, gen_disciplinary_notice())
        tick("HR-Disc"); generated += 1

    # Benefits Enrollment
    for i in range(60):
        dt = rdate(2016, 2026)
        fname = f"benefits_enrollment_{rname().replace(' ','_')}_{dt.year}.txt"
        subdir = "HR/Benefits/Enrollment" if dt.year >= 2020 else "HR/Benefits/Archive"
        write_file(BASE / subdir / fname, gen_benefits_enrollment())
        tick("HR-Ben"); generated += 1

    # Training Records
    for i in range(60):
        dt = rdate(2016, 2026)
        fname = f"training_record_{rname().replace(' ','_')}_{dt.year}.txt"
        write_file(BASE / "HR/Training" / fname, gen_training_record())
        tick("HR-Train"); generated += 1

    # Exit Interviews
    for i in range(30):
        dt = rdate(2016, 2026)
        fname = f"exit_interview_{rname().replace(' ','_')}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / "HR/Offboarding" / fname, gen_exit_interview())
        tick("HR-Exit"); generated += 1

    # NW-4 Forms
    for i in range(40):
        dt = rdate(2016, 2026)
        fname = f"nw4_withholding_{rname().replace(' ','_')}_{dt.year}.txt"
        write_file(BASE / "HR/Onboarding" / fname, gen_nw4_form())
        tick("HR-NW4"); generated += 1

    # Onboarding Packets
    for i in range(40):
        dt = rdate(2016, 2026)
        fname = f"onboarding_packet_{rname().replace(' ','_')}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / "HR/Onboarding" / fname, gen_onboarding_packet())
        tick("HR-Onb"); generated += 1

    return generated

print("Starting NorthStar document generation...")
hr_count = generate_hr_documents()
print(f"HR documents done: {hr_count}")

# ─── MEDICAL DOCUMENT GENERATORS ─────────────────────────────────────────────

def gen_patient_registration():
    name = rname()
    dob = rdob()
    dt = rdate(2016, 2026)
    yr = dt.year
    org = get_org(yr)
    mrn = rmrn()
    insurer = random.choice(INSURANCE_COMPANIES)
    physician = random.choice(PHYSICIANS)
    content = f"""{org}
PATIENT REGISTRATION FORM
Date: {dt.strftime('%m/%d/%Y')}
MRN: {mrn}
EHR System: {get_ehr(yr)}

PATIENT DEMOGRAPHICS
Full Name: {name}
Date of Birth: {dob.strftime('%m/%d/%Y')}
Age: {int((dt - dob).days / 365)}
Gender: {random.choice(['Male','Female','Non-binary','Unknown'])}
SSN: {rssn()}
Address: {raddress()}
Phone (Home): {rphone()}
Phone (Mobile): {rphone()}
Email: {remail(name)}
Preferred Language: {random.choice(['English','Spanish','English','Mandarin','English','Vietnamese'])}
Race/Ethnicity: {random.choice(['White/Non-Hispanic','Hispanic/Latino','Black/African American','Asian','Multiracial','Prefer not to disclose'])}
Marital Status: {random.choice(['Single','Married','Divorced','Widowed','Domestic Partnership'])}

INSURANCE INFORMATION
Primary Insurance: {insurer}
Member ID: MBR-{random.randint(100000000,999999999)}
Group Number: GRP-{random.randint(10000,99999)}
Subscriber Name: {random.choice([name, rname()])}
Subscriber DOB: {rdob().strftime('%m/%d/%Y')}
Relationship: {random.choice(['Self','Spouse','Parent','Child'])}

Secondary Insurance: {random.choice(['None'] + INSURANCE_COMPANIES)}

EMERGENCY CONTACT
Name: {rname()}
Relationship: {random.choice(['Spouse','Parent','Sibling','Friend','Partner'])}
Phone: {rphone()}

REFERRING PHYSICIAN: {random.choice(PHYSICIANS + ['Self-Referred','None'])}
PRIMARY CARE PHYSICIAN: {physician}
ASSIGNED PROVIDER: {physician}

HIPAA Authorization Signed: {random.choice(['Yes','Yes','Yes','No — patient declined'])}
"""
    return maybe_typo(content)


def gen_soap_note():
    physician = random.choice(PHYSICIANS)
    dt = rdate(2016, 2026)
    yr = dt.year
    org = get_org(yr)
    mrn = rmrn()
    patient_name = rname()
    dob = rdob()
    diag_code, diag_name = random.choice(DIAGNOSES)
    cpt_code, cpt_desc = random.choice(CPT_CODES)
    meds = random.sample(MEDICATIONS, random.randint(1, 4))
    content = f"""{org} — CLINICAL DOCUMENTATION
OFFICE VISIT NOTE
Date of Service: {dt.strftime('%m/%d/%Y')}
MRN: {mrn}
Patient: {patient_name}
DOB: {dob.strftime('%m/%d/%Y')}
Provider: {physician}
EHR: {get_ehr(yr)}

SUBJECTIVE
Chief Complaint: {random.choice([
    'Follow-up for hypertension management',
    'Cough and congestion for 5 days',
    'Knee pain, worsening over 3 weeks',
    'Annual wellness examination',
    'Fatigue and headache x 2 weeks',
    'Abdominal pain, intermittent',
    'Rash on forearm, onset 4 days ago',
    'Shortness of breath with exertion',
    'Routine diabetes management visit',
    'Back pain, lower lumbar, 10 days',
])}
HPI: Patient is a {int((dt - dob).days / 365)}-year-old {random.choice(['male','female'])} presenting with the above complaint. {random.choice([
    'Symptoms began gradually without identifiable precipitant.',
    'Patient reports symptoms started after strenuous activity.',
    'Onset was acute. Patient denies fever or chills.',
    'Symptoms have been persistent and progressive.',
    'Patient was seen last {random.choice(["month","quarter","year"])} for similar concern.',
])}
PMH: {random.choice(['Hypertension, Type 2 Diabetes','No significant past medical history','Asthma, seasonal allergies','Hyperlipidemia','Depression, anxiety'])}
Medications: {'; '.join(meds)}
Allergies: {random.choice(['NKDA','Penicillin — hives','Sulfa — rash','Aspirin — GI intolerance','NKDA'])}
Social Hx: {random.choice(['Non-smoker, occasional alcohol','Former smoker, quit 2018','Denies tobacco, alcohol, illicit drugs','1-2 drinks/week, non-smoker'])}

OBJECTIVE
Vital Signs:
  BP: {random.randint(105,160)}/{random.randint(60,100)} mmHg
  HR: {random.randint(58,105)} bpm
  RR: {random.randint(12,22)} breaths/min
  Temp: {round(random.uniform(97.2, 101.4), 1)} F
  SpO2: {random.randint(94,100)}%
  Weight: {random.randint(110,280)} lbs
  Height: {random.randint(60,76)} in

General: {random.choice(['Alert and oriented x3, no acute distress','Well-appearing, cooperative','Mildly distressed, appropriate for presentation'])}
HEENT: {random.choice(['Normocephalic, atraumatic, PERRL','Conjunctivae clear, TMs intact','Oropharynx without erythema'])}
Cardiovascular: {random.choice(['RRR, no murmurs, rubs, or gallops','Regular rate and rhythm','S1/S2 normal, no extra heart sounds'])}
Respiratory: {random.choice(['Clear to auscultation bilaterally','Mild expiratory wheeze noted bilaterally','CTA bilaterally, no rales'])}
Abdomen: {random.choice(['Soft, non-tender, non-distended','Mild epigastric tenderness','BS present x4 quadrants, no organomegaly'])}
Extremities: {random.choice(['No edema, cyanosis, or clubbing','Mild bilateral lower extremity edema','Normal ROM, no deformities'])}

ASSESSMENT
Diagnosis: {diag_name}
ICD-10: {diag_code}

PLAN
1. {random.choice(meds)} — continue current regimen
2. {random.choice(['Labs ordered — see attached requisition','Follow-up in 4-6 weeks','Referral to specialist placed','Imaging ordered — see below','Patient counseled on lifestyle modifications'])}
3. {random.choice(['Return to clinic if symptoms worsen','Education provided regarding diagnosis','Prescription sent to pharmacy of choice','Patient verbalized understanding of plan'])}

CPT: {cpt_code} — {cpt_desc}
Time spent: {random.randint(15,45)} minutes
Complexity: {random.choice(['Low','Moderate','High'])}

Electronically signed: {physician}
Date/Time: {dt.strftime('%m/%d/%Y')} {random.randint(8,17):02d}:{random.randint(0,59):02d}
"""
    return maybe_typo(content)


def gen_lab_report():
    physician = random.choice(PHYSICIANS)
    dt = rdate(2016, 2026)
    yr = dt.year
    org = get_org(yr)
    mrn = rmrn()
    patient_name = rname()
    dob = rdob()
    panel = random.choice(["Complete Blood Count (CBC)","Comprehensive Metabolic Panel (CMP)",
        "Lipid Panel","HbA1c","Thyroid Panel","Urinalysis"])

    def lab_val(ref_range):
        lo_str, hi_str = ref_range.replace('%','').replace(' mIU/L','').replace(' K/uL','').replace(' M/uL','').replace(' g/dL','').replace(' mEq/L','').replace(' mg/dL','').split('-') if '-' in ref_range else (ref_range.replace('<','').replace('>',''), ref_range.replace('<','').replace('>',''))
        try:
            lo, hi = float(lo_str.strip()), float(hi_str.strip())
            val = round(random.uniform(lo*0.85, hi*1.15), 1)
            flag = " [H]" if val > hi else " [L]" if val < lo else ""
            return f"{val}{flag}"
        except:
            return "See result"

    results = "\n".join(f"  {name:<30} {lab_val(ref):<15} Ref: {ref}" for name, ref in random.sample(LAB_TESTS, min(8, len(LAB_TESTS))))
    content = f"""{org} — LABORATORY SERVICES
LAB REPORT
Accession #: LAB-{random.randint(1000000,9999999)}
Date Collected: {dt.strftime('%m/%d/%Y')} {random.randint(6,14):02d}:{random.randint(0,59):02d}
Date Reported: {dt.strftime('%m/%d/%Y')} {random.randint(14,22):02d}:{random.randint(0,59):02d}

Patient: {patient_name}
MRN: {mrn}
DOB: {dob.strftime('%m/%d/%Y')}
Ordering Provider: {physician}

PANEL: {panel}

RESULTS
{results}

SPECIMEN QUALITY: {random.choice(['Acceptable','Hemolyzed — results may be affected','Acceptable','Acceptable','Lipemic'])}
PERFORMING LAB: NorthStar Regional Laboratory Services
LAB DIRECTOR: {random.choice(PHYSICIANS)}

INTERPRETATION: {random.choice([
    'Results within normal limits. No immediate action required.',
    'One or more values flagged. Clinical correlation recommended.',
    'Abnormal result noted. Provider has been notified.',
    'Results consistent with previously established baseline.',
])}

Verified by: Lab Tech {rname()}
"""
    return content


def gen_radiology_report():
    physician = random.choice(PHYSICIANS)
    radiologist = random.choice(PHYSICIANS)
    dt = rdate(2016, 2026)
    yr = dt.year
    org = get_org(yr)
    mrn = rmrn()
    patient_name = rname()
    dob = rdob()
    study = random.choice([
        ("Chest X-Ray PA and Lateral","71046","Chest PA/LAT"),
        ("CT Abdomen and Pelvis with Contrast","74177","CT Abd/Pelvis+C"),
        ("MRI Brain without Contrast","70551","MRI Brain-C"),
        ("X-Ray Right Knee AP/Lateral","73560","XR Knee RT"),
        ("CT Head without Contrast","70450","CT Head-C"),
        ("X-Ray Lumbar Spine","72100","XR L-Spine"),
    ])
    findings = {
        "Chest X-Ray PA and Lateral": random.choice([
            "Lungs are clear. Heart size normal. No pleural effusion or pneumothorax. Bony structures intact.",
            "Mild cardiomegaly. No acute pulmonary infiltrate. No pleural effusion.",
            "Subtle right lower lobe haziness, possible early infiltrate. No effusion.",
        ]),
        "CT Abdomen and Pelvis with Contrast": random.choice([
            "No acute intraabdominal process. Liver, spleen, kidneys unremarkable. No free air or fluid.",
            "3mm non-obstructing calculus in right ureter. Remainder of study unremarkable.",
            "Mild diffuse hepatic steatosis. No focal hepatic lesion. Gallbladder without stones.",
        ]),
        "MRI Brain without Contrast": random.choice([
            "No acute intracranial pathology. No mass, midline shift, or hemorrhage.",
            "Scattered periventricular white matter T2 hyperintensities, likely chronic small vessel ischemic change.",
            "Normal brain MRI. Paranasal sinuses clear.",
        ]),
        "X-Ray Right Knee AP/Lateral": random.choice([
            "Mild medial compartment joint space narrowing. No acute fracture. Small osteophyte formation.",
            "No fracture or dislocation. Soft tissue swelling noted. Joint space preserved.",
            "Moderate tricompartmental osteoarthritic changes. No acute osseous injury.",
        ]),
        "CT Head without Contrast": random.choice([
            "No acute intracranial abnormality. No hemorrhage, edema, or mass.",
            "Age-appropriate cerebral volume loss. No acute finding.",
        ]),
        "X-Ray Lumbar Spine": random.choice([
            "Mild L4-L5 disc space narrowing. No acute fracture. Alignment preserved.",
            "Degenerative changes throughout lumbar spine, most pronounced at L5-S1. No spondylolisthesis.",
        ]),
    }
    content = f"""{org} — RADIOLOGY
RADIOLOGY REPORT
Study Date: {dt.strftime('%m/%d/%Y')}
Accession: RAD-{random.randint(1000000,9999999)}
Study: {study[0]}
CPT: {study[1]}

Patient: {patient_name}
MRN: {mrn}
DOB: {dob.strftime('%m/%d/%Y')}
Ordering Provider: {physician}
Clinical Indication: {random.choice(['Chest pain, r/o pneumonia','Abdominal pain, r/o obstruction','Headache, r/o intracranial pathology','Knee pain after fall','Trauma evaluation','Back pain, radiculopathy symptoms'])}

TECHNIQUE
{study[2]} performed using standard departmental protocol. {random.choice(['Contrast administered without adverse reaction.','No contrast administered.','Patient tolerated procedure well.'])}

FINDINGS
{findings.get(study[0], 'Study within normal limits.')}

IMPRESSION
{random.choice([
    '1. No acute pathology identified.',
    '1. Findings as described above. Recommend clinical correlation.',
    '1. Mild degenerative changes. No acute findings.',
    '1. Unremarkable study.',
    '1. Incidental finding noted — recommend follow-up as clinically indicated.',
])}

RADIOLOGIST: {radiologist}
Signed: {dt.strftime('%m/%d/%Y')} {random.randint(8,20):02d}:{random.randint(0,59):02d}
"""
    return content


def gen_discharge_summary():
    physician = random.choice(PHYSICIANS)
    dt = rdate(2016, 2026)
    yr = dt.year
    org = get_org(yr)
    mrn = rmrn()
    patient_name = rname()
    dob = rdob()
    los = random.randint(1, 14)
    admit = dt - timedelta(days=los)
    diag_code, diag_name = random.choice(DIAGNOSES)
    meds = random.sample(MEDICATIONS, random.randint(2, 5))
    content = f"""{org}
DISCHARGE SUMMARY
MRN: {mrn}
Patient: {patient_name}
DOB: {dob.strftime('%m/%d/%Y')}
Admission Date: {admit.strftime('%m/%d/%Y')}
Discharge Date: {dt.strftime('%m/%d/%Y')}
Length of Stay: {los} day(s)
Admitting Physician: {physician}
Attending at Discharge: {physician}
Unit: {random.choice(['3-East Medical/Surgical','4-West Telemetry','ICU','2-North Observation','6-South Oncology'])}

ADMITTING DIAGNOSIS: {diag_name} ({diag_code})
DISCHARGE DIAGNOSIS: {diag_name} ({diag_code})
{f'Secondary Diagnosis: {random.choice(DIAGNOSES)[1]}' if random.random() > 0.5 else ''}

HOSPITAL COURSE
Patient was admitted for management of {diag_name}. {random.choice([
    'Initial workup included laboratory studies and imaging.',
    'Patient was started on IV antibiotics and monitored for clinical response.',
    'Cardiology was consulted and recommended further evaluation.',
    'Patient responded well to initial therapy and was transitioned to oral medications.',
    'Physical therapy was involved in care and patient demonstrated improvement in functional status.',
])} Patient remained hemodynamically stable throughout the admission. Condition improved and patient was cleared for discharge to {random.choice(['home','home with home health','skilled nursing facility','rehabilitation facility'])}.

DISCHARGE MEDICATIONS
{chr(10).join(f'  {i+1}. {m}' for i, m in enumerate(meds))}

DISCHARGE INSTRUCTIONS
Diet: {random.choice(['Regular diet','Low sodium','Diabetic diet','Cardiac diet','Clear liquids x48 hours then advance as tolerated'])}
Activity: {random.choice(['As tolerated','Light activity only x2 weeks','No lifting > 10 lbs for 6 weeks','Bed rest x72 hours'])}
Follow-up: {random.choice(PHYSICIANS)} in {random.randint(3,14)} days

Return to ED if: chest pain, shortness of breath, fever >101F, worsening symptoms

Patient education provided: {random.choice(['Yes, patient verbalized understanding','Yes, written instructions given','Yes, interpreter services used'])}

Discharge Condition: {random.choice(['Good','Fair','Stable'])}
Signed: {physician}    {dt.strftime('%m/%d/%Y')}
"""
    return maybe_typo(content)


def gen_billing_statement():
    dt = rdate(2016, 2026)
    yr = dt.year
    org = get_org(yr)
    mrn = rmrn()
    patient_name = rname()
    insurer = random.choice(INSURANCE_COMPANIES)
    services = random.sample(CPT_CODES, random.randint(1, 4))
    total = sum(random.randint(80, 1200) for _ in services)
    ins_paid = int(total * random.uniform(0.5, 0.9))
    balance = total - ins_paid
    content = f"""{org}
PATIENT BILLING STATEMENT
Statement Date: {dt.strftime('%m/%d/%Y')}
Account Number: ACCT-{random.randint(1000000,9999999)}
MRN: {mrn}

PATIENT: {patient_name}
Address: {raddress()}

INSURANCE: {insurer}
Member ID: MBR-{random.randint(100000000,999999999)}

DATE OF SERVICE: {(dt - timedelta(days=random.randint(1,30))).strftime('%m/%d/%Y')}
Provider: {random.choice(PHYSICIANS)}

CHARGES
{'Code':<10} {'Description':<45} {'Amount':>10}
{'-'*70}
"""
    for code, desc in services:
        amt = random.randint(80, 1200)
        content += f"{code:<10} {desc:<45} ${amt:>8,}\n"
    content += f"""
{'-'*70}
Total Charges:              ${total:>8,}
Insurance Payment:         -${ins_paid:>8,}
Adjustments:               -${random.randint(0, int(total*0.1)):>8,}
Patient Balance Due:        ${balance:>8,}

PAYMENT DUE BY: {(dt + timedelta(days=30)).strftime('%m/%d/%Y')}
To pay by phone: (555) 400-BILL
To pay online: northstar-health.internal/pay
"""
    return content


def gen_nursing_note():
    nurse = rname()
    dt = rdate(2016, 2026)
    yr = dt.year
    org = get_org(yr)
    mrn = rmrn()
    patient_name = rname()
    content = f"""{org} — NURSING DOCUMENTATION
NURSING NOTE
Date/Time: {dt.strftime('%m/%d/%Y')} {random.randint(6,22):02d}:{random.randint(0,59):02d}
MRN: {mrn}
Patient: {patient_name}
Unit: {random.choice(['3-East','4-West','ICU','2-North Obs','ED','PACU'])}
RN: {nurse}

NOTE TYPE: {random.choice(['Shift Assessment','Medication Administration','Patient Education','Incident Report Follow-Up','Discharge Teaching','IV Site Assessment'])}

{random.choice([
    f'Patient alert and oriented x{random.randint(1,3)}. Vital signs stable. Tolerated oral medications without difficulty. Voiding without difficulty. Ambulated in hall x2 with minimal assistance.',
    f'Patient reports pain {random.randint(3,8)}/10, treated with prescribed analgesic with relief to {random.randint(1,4)}/10. Patient repositioned. Call light within reach.',
    f'IV site assessed — {random.choice(["no signs of infiltration or phlebitis","mild erythema noted, site changed to right AC","patent and flushing well"])}. IV fluid infusing at {random.randint(75,125)} mL/hr.',
    f'Patient education completed regarding {random.choice(["home medication regimen","wound care instructions","diabetic diet","blood pressure monitoring","fall prevention"])}. Patient verbalized understanding.',
    f'Patient ambulated to bathroom independently. No distress noted. Vital signs reassessed and stable. Family updated by RN.',
])}

Shift Vitals:
  BP: {random.randint(105,155)}/{random.randint(60,95)} mmHg | HR: {random.randint(58,100)} | RR: {random.randint(12,20)} | Temp: {round(random.uniform(97.5,100.2),1)}F | SpO2: {random.randint(95,100)}%

Plan: Continue current orders per physician. Reassess in {random.randint(2,4)} hours.
Signature: {nurse}, RN    EHR: {get_ehr(yr)}
"""
    return maybe_typo(content)


def gen_care_plan():
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    mrn = rmrn()
    patient_name = rname()
    physician = random.choice(PHYSICIANS)
    diag_code, diag_name = random.choice(DIAGNOSES)
    goals = [
        "Patient will demonstrate stable vital signs within normal range within 48 hours.",
        "Patient will verbalize understanding of medication regimen before discharge.",
        "Patient will ambulate 100 feet independently by day 3 of admission.",
        "Patient will maintain blood glucose 80-180 mg/dL throughout stay.",
        "Patient will demonstrate wound care technique independently prior to discharge.",
        "Patient will report pain < 4/10 on numeric pain scale with current regimen.",
    ]
    interventions = [
        "Vital signs every 4 hours and PRN.",
        "Administer medications per physician orders and document response.",
        "Daily weights and fluid balance monitoring.",
        "Consult physical therapy for mobility assessment and planning.",
        "Skin integrity assessment each shift, reposition every 2 hours.",
        "Patient education regarding diagnosis, medications, and follow-up care.",
        "Fall risk assessment each shift — implement precautions as indicated.",
    ]
    content = f"""{org}
INTERDISCIPLINARY CARE PLAN
MRN: {mrn}
Patient: {patient_name}
Date Initiated: {dt.strftime('%m/%d/%Y')}
Primary Diagnosis: {diag_name} ({diag_code})
Attending: {physician}
Care Coordinator: {rname()}, RN Case Manager

PATIENT GOALS
{chr(10).join(f'  {i+1}. {g}' for i, g in enumerate(random.sample(goals, 3)))}

NURSING INTERVENTIONS
{chr(10).join(f'  - {v}' for v in random.sample(interventions, 4))}

MULTIDISCIPLINARY TEAM
  Attending Physician: {physician}
  Primary Nurse: {rname()}, RN
  Case Manager: {rname()}, RN
  Social Work: {random.choice(['Consulted','Not indicated','Pending referral'])}
  Nutrition: {random.choice(['Dietitian consulted','Standard diet ordered','NPO per surgeon'])}
  Physical Therapy: {random.choice(['Active','Consulted — pending eval','Not indicated'])}

Review Date: {(dt + timedelta(days=1)).strftime('%m/%d/%Y')}
"""
    return content


def gen_telehealth_record():
    dt = rdate(2020, 2026)
    org = get_org(dt.year)
    mrn = rmrn()
    patient_name = rname()
    physician = random.choice(PHYSICIANS)
    platform = random.choice(["Zoom Health Pro","Doxy.me","NovaMed Telehealth","VSee Clinic"])
    content = f"""{org}
TELEHEALTH VISIT RECORD
Date of Service: {dt.strftime('%m/%d/%Y')}
MRN: {mrn}
Patient: {patient_name}
DOB: {rdob().strftime('%m/%d/%Y')}
Provider: {physician}
Visit Type: Telehealth — {random.choice(['Video','Phone'])}
Platform: {platform}
Duration: {random.randint(10,45)} minutes

CONSENT OBTAINED: {random.choice(['Yes — verbal consent documented','Yes — electronic consent on file'])}
PATIENT LOCATION: {random.choice(CITIES)}, {STATE}
PROVIDER LOCATION: NorthStar Regional Health Network Campus

CHIEF COMPLAINT: {random.choice([
    'Medication refill request and symptom check-in',
    'Follow-up for recent lab results',
    'New complaint — fatigue and headache',
    'Chronic disease management — diabetes',
    'Mental health follow-up',
    'Post-discharge check-in',
])}

{random.choice([
    'Patient was seen via video platform. Audio and video quality adequate throughout visit. Patient appeared comfortable and communicated clearly.',
    'Patient called in by phone — video was not available due to technical difficulties. Clinical assessment completed via telephone. Limitations of phone-only visit discussed.',
])}

Assessment and Plan: {random.choice(DIAGNOSES)[1]} — continuing current management. {random.choice(['New prescription sent electronically to pharmacy on file.','No medication changes at this time.','Labs ordered via patient portal.','Referral placed.'])}

Follow-up: {random.randint(2,8)} weeks {random.choice(['telehealth','in-person','patient preference'])}
Billing: {random.choice(['99213','99214','99441','99442'])} — Telehealth Modifier GT
Signed: {physician}
"""
    return content


def gen_mental_health_intake():
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    mrn = rmrn()
    patient_name = rname()
    physician = random.choice(PHYSICIANS)
    content = f"""{org} — BEHAVIORAL HEALTH SERVICES
MENTAL HEALTH INTAKE ASSESSMENT
Date: {dt.strftime('%m/%d/%Y')}
MRN: {mrn}
Patient: {patient_name}
DOB: {rdob().strftime('%m/%d/%Y')}
Clinician: {physician}

PRESENTING CONCERNS
{random.choice([
    'Patient presents reporting persistent sadness, low energy, and difficulty concentrating for approximately 6 weeks. Denies current suicidal ideation.',
    'Patient reports excessive worry and anxious thoughts that interfere with daily functioning. Sleep disrupted. Appetite decreased.',
    'Patient referred by PCP following screening positive on PHQ-9 for moderate depression.',
    'Patient requests support following recent significant life stressor. Reports difficulty coping.',
    'Evaluation requested by employer following workplace incident.',
])}

PHQ-9 Score: {random.randint(0,27)} — {random.choice(['Minimal','Mild','Moderate','Moderately Severe','Severe'])} Depression
GAD-7 Score: {random.randint(0,21)} — {random.choice(['Minimal','Mild','Moderate','Severe'])} Anxiety

RISK ASSESSMENT
Suicidal Ideation: {random.choice(['Denies','Passive ideation only — no plan or intent','None reported'])}
Homicidal Ideation: Denies
Self-Harm History: {random.choice(['None reported','Remote history — not current','None'])}
Safety Plan: {random.choice(['Developed and reviewed with patient','Not indicated','On file from prior encounter'])}

MENTAL STATUS EXAM
Appearance: {random.choice(['Well-groomed, appropriate dress','Casually dressed, adequate hygiene','Disheveled appearance'])}
Mood: {random.choice(['Depressed','Anxious','Euthymic','Labile','Dysthymic'])}
Affect: {random.choice(['Congruent with mood','Flat','Blunted','Full range'])}
Thought Process: {random.choice(['Linear and goal-directed','Mildly tangential','Organized'])}
Insight: {random.choice(['Good','Fair','Limited'])}

DIAGNOSIS: {random.choice(['F32.1 — Major Depressive Disorder, Moderate','F41.1 — Generalized Anxiety Disorder','F43.10 — PTSD, unspecified','F32.0 — Major Depressive Disorder, Mild','Z13.89 — Screening encounter'])}

PLAN
Psychotherapy: {random.choice(['Individual therapy weekly x8 sessions','CBT recommended','DBT skills group referral made'])}
Medication: {random.choice(['Sertraline 50mg daily initiated','No medication at this time','Discussed with prescribing provider'])}
Next Appointment: {(dt + timedelta(days=random.randint(7,21))).strftime('%m/%d/%Y')}
"""
    return maybe_typo(content)


def gen_immunization_record():
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    mrn = rmrn()
    patient_name = rname()
    vaccines = [
        ("Influenza (Flu)","IIV4","0.5mL IM"),
        ("COVID-19 mRNA","Moderna","0.5mL IM"),
        ("Tdap","Adacel","0.5mL IM"),
        ("Pneumococcal","PCV15","0.5mL IM"),
        ("Hepatitis B","Engerix-B","1.0mL IM"),
        ("Zoster","Shingrix","0.5mL IM"),
        ("MMR","M-M-R II","0.5mL SubQ"),
    ]
    given = random.sample(vaccines, random.randint(1, 4))
    vax_block = "\n".join(f"  {v[0]:<25} {v[1]:<15} {v[2]:<12} Lot: {rserial()[:6]}  Site: {random.choice(['L deltoid','R deltoid','L thigh'])}" for v in given)
    content = f"""{org}
IMMUNIZATION RECORD
Date: {dt.strftime('%m/%d/%Y')}
MRN: {mrn}
Patient: {patient_name}
DOB: {rdob().strftime('%m/%d/%Y')}
Provider: {random.choice(PHYSICIANS)}

VACCINES ADMINISTERED TODAY
{vax_block}

VIS Forms Given: Yes
Patient/Guardian consent obtained: Yes
Next Due: Per CDC schedule — see patient portal

Administered by: {rname()}, RN
"""
    return content


def gen_covid_screening():
    dt = rdate(2020, 2022)
    org = get_org(dt.year)
    name = rname()
    content = f"""{org}
COVID-19 VISITOR / STAFF SCREENING FORM
Date: {dt.strftime('%m/%d/%Y')}

Name: {name}
Role: {random.choice(['Visitor','Staff','Vendor','Contractor'])}
Department/Destination: {random.choice(DEPARTMENTS)}

SCREENING QUESTIONS
1. Do you have fever (>100.4F) or chills? {random.choice(['No','No','No','Yes'])}
2. New cough? {random.choice(['No','No','No','Yes'])}
3. Shortness of breath? {random.choice(['No','No','No','Yes'])}
4. New loss of taste or smell? {random.choice(['No','No','No','Yes'])}
5. Known COVID-19 exposure in past 14 days? {random.choice(['No','No','No','Yes'])}
6. Positive COVID-19 test in past 10 days? No

Temperature Taken: {round(random.uniform(97.2, 99.0), 1)}F

SCREENING RESULT: {random.choice(['CLEARED TO ENTER','CLEARED TO ENTER','CLEARED TO ENTER','DENIED ENTRY — Symptom(s) reported'])}

Screened by: {rname()}
PPE Issued: {random.choice(['Surgical mask provided','Staff wearing own PPE','N95 required — issued at nursing station'])}
"""
    return content


def generate_medical_documents():
    generated = 0

    # Patient registrations
    for i in range(120):
        dt = rdate(2016, 2026)
        yr = dt.year
        subdir = f"Patients/{yr}"
        fname = f"patient_registration_MRN{random.randint(10000000,99999999)}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / subdir / fname, gen_patient_registration())
        tick("Med-Reg"); generated += 1

    # Active patient folders
    for i in range(50):
        dt = rdate(2022, 2026)
        fname = f"registration_active_{rmrn()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / "Patients/Active" / fname, gen_patient_registration())
        tick("Med-Reg"); generated += 1

    # SOAP Notes
    for i in range(200):
        dt = rdate(2016, 2026)
        yr = dt.year
        subdir = f"Patients/{yr}"
        fname = f"soap_note_{rmrn()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / subdir / fname, gen_soap_note())
        tick("Med-SOAP"); generated += 1

    # Lab Reports
    for i in range(150):
        dt = rdate(2016, 2026)
        yr = dt.year
        subdir = random.choice([f"Patients/{yr}", f"Billing/{yr}"])
        fname = f"lab_report_{rmrn()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / subdir / fname, gen_lab_report())
        tick("Med-Lab"); generated += 1

    # Radiology Reports
    for i in range(80):
        dt = rdate(2016, 2026)
        yr = dt.year
        fname = f"radiology_report_{rmrn()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / f"Patients/{yr}" / fname, gen_radiology_report())
        tick("Med-Rad"); generated += 1

    # Discharge Summaries
    for i in range(100):
        dt = rdate(2016, 2026)
        yr = dt.year
        subdir = random.choice([f"Patients/{yr}", "Patients/Archived"])
        fname = f"discharge_summary_{rmrn()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / subdir / fname, gen_discharge_summary())
        tick("Med-Disch"); generated += 1

    # Billing Statements
    for yr in range(2016, 2027):
        count = random.randint(10, 25) if yr < 2026 else 5
        for i in range(count):
            dt = rdate(yr, yr)
            fname = f"billing_statement_{rmrn()}_{dt.strftime('%Y%m%d')}.txt"
            write_file(BASE / f"Billing/{yr}" / fname, gen_billing_statement())
            tick("Med-Bill"); generated += 1

    # Nursing Notes
    for i in range(80):
        dt = rdate(2016, 2026)
        yr = dt.year
        fname = f"nursing_note_{rmrn()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / f"Patients/{yr}" / fname, gen_nursing_note())
        tick("Med-Nrs"); generated += 1

    # Care Plans
    for i in range(50):
        dt = rdate(2018, 2026)
        yr = dt.year
        fname = f"care_plan_{rmrn()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / f"Patients/{yr}" / fname, gen_care_plan())
        tick("Med-Care"); generated += 1

    # Telehealth Records
    for i in range(60):
        dt = rdate(2020, 2026)
        yr = dt.year
        fname = f"telehealth_visit_{rmrn()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / f"Patients/{yr}" / fname, gen_telehealth_record())
        tick("Med-TH"); generated += 1

    # Mental Health Intakes
    for i in range(40):
        dt = rdate(2016, 2026)
        yr = dt.year
        fname = f"mh_intake_{rmrn()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / f"Patients/{yr}" / fname, gen_mental_health_intake())
        tick("Med-MH"); generated += 1

    # Immunization Records
    for i in range(50):
        dt = rdate(2016, 2026)
        yr = dt.year
        fname = f"immunization_record_{rmrn()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / f"Patients/{yr}" / fname, gen_immunization_record())
        tick("Med-Vax"); generated += 1

    # COVID screening forms
    for i in range(40):
        dt = rdate(2020, 2022)
        fname = f"covid_screening_{rname().replace(' ','_')}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / "Patients/Active" / fname, gen_covid_screening())
        tick("Med-Covid"); generated += 1

    # Insurance verification
    for i in range(60):
        dt = rdate(2016, 2026)
        mrn = rmrn()
        patient_name = rname()
        insurer = random.choice(INSURANCE_COMPANIES)
        plan_type = random.choice(['PPO','HMO','HDHP'])
        content = f"""NorthStar Regional Health Network
INSURANCE VERIFICATION FORM
Date Verified: {dt.strftime('%m/%d/%Y')}
MRN: {mrn}
Patient: {patient_name}
Insurance: {insurer}
Plan Type: {plan_type}
Member ID: MBR-{random.randint(100000000,999999999)}
Group: GRP-{random.randint(10000,99999)}
Effective Date: {rdate(dt.year-1, dt.year).strftime('%m/%d/%Y')}
Copay: ${random.choice([20,25,30,40,50])}
Deductible: ${random.randint(500,5000):,} (Met: ${random.randint(0,3000):,})
Out-of-Pocket Max: ${random.randint(2000,9000):,}
Prior Auth Required: {random.choice(['Yes','No','Depends on service'])}
Verified by: {rname()}
"""
        fname = f"insurance_verification_{mrn}_{dt.strftime('%Y%m%d')}.txt"
        subdir = "Insurance/Verification" if random.random() > 0.4 else "Insurance/Claims"
        write_file(BASE / subdir / fname, content)
        tick("Med-Ins"); generated += 1

    return generated

print("Starting medical document generation...")
med_count = generate_medical_documents()
print(f"Medical documents done: {med_count}")

# ─── IT DOCUMENT GENERATORS ──────────────────────────────────────────────────

def gen_help_desk_ticket():
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    requester = rname()
    ticket_id = f"INC-{random.randint(10000,99999)}"
    issue_types = [
        ("Password Reset", "User is unable to log into their workstation. Password may be expired or account locked.",
         "Account unlocked and temporary password issued. User prompted to change at next login."),
        ("Printer Not Responding", "Printer on 3rd floor nursing station is offline and not printing. Multiple users affected.",
         "Print spooler restarted. Driver reinstalled. Printer back online."),
        ("VPN Connection Failure", "User unable to connect to VPN from home. Error: 'Authentication failed'.",
         "VPN client updated to version 4.2.1. Certificate renewed. Connection confirmed working."),
        ("Email Not Sending", "User reports outbound emails are stuck in outbox. Problem started this morning.",
         "Outlook profile rebuilt. Issue resolved. User confirmed email sending normally."),
        ("Software Installation", "User requesting installation of Adobe Acrobat Pro for contract review purposes.",
         "Installation completed after manager approval received. License applied."),
        ("Computer Running Slowly", "Workstation in billing department running extremely slowly, affecting productivity.",
         "Disk cleanup performed. 14 pending Windows updates installed. Performance improved."),
        ("Phishing Email Received", "User received suspicious email asking them to verify credentials via external link. Did not click.",
         "Email quarantined. Security team notified. User commended for correct reporting."),
        ("Monitor Not Working", "Second monitor stopped displaying after workstation was moved to new location.",
         "DisplayPort cable was loose. Reseated and confirmed working."),
        ("MFA Not Working", "Multi-factor authentication app not generating codes. User locked out of EHR.",
         "MFA device re-enrolled. Backup codes provided. Access restored."),
        ("New Employee Setup", f"New employee {rname()} starting {(dt + timedelta(days=7)).strftime('%m/%d/%Y')} needs workstation, EHR access, and email.",
         "Workstation imaged and deployed. Email created. EHR provisioning in progress."),
    ]
    itype, desc, resolution = random.choice(issue_types)
    status = random.choice(["Open","Closed","Closed","Closed","In Progress","Pending User Response"])
    priority = random.choice(["P1 - Critical","P2 - High","P3 - Medium","P4 - Low"])
    content = f"""{org}
IT HELP DESK TICKET
Ticket ID: {ticket_id}
Date Opened: {dt.strftime('%m/%d/%Y')} {random.randint(7,17):02d}:{random.randint(0,59):02d}
Status: {status}
Priority: {priority}

REQUESTER INFORMATION
Name: {requester}
Employee ID: {rempid()}
Department: {random.choice(DEPARTMENTS)}
Phone: {rphone()}
Email: {remail(requester)}
Location: {random.choice(['Building A Room 204','Nursing Station 3E','IT Lab B101','Remote — Home Office','Clinic B Suite 12','Admin Wing 2nd Floor'])}

ISSUE CATEGORY: {itype}
DESCRIPTION:
{desc}

ASSIGNED TECHNICIAN: {rname()}
Assignment Date: {dt.strftime('%m/%d/%Y')}

WORK LOG
[{dt.strftime('%m/%d/%Y')} {random.randint(8,17):02d}:{random.randint(0,59):02d}] Ticket received. Contacted user.
[{(dt + timedelta(hours=random.randint(1,4))).strftime('%m/%d/%Y')} {random.randint(8,17):02d}:{random.randint(0,59):02d}] On-site or remote session initiated.
[{(dt + timedelta(hours=random.randint(2,8))).strftime('%m/%d/%Y')} {random.randint(8,17):02d}:{random.randint(0,59):02d}] {resolution}

RESOLUTION NOTES: {resolution}
Date Closed: {(dt + timedelta(hours=random.randint(1,48))).strftime('%m/%d/%Y') if status == 'Closed' else 'Open'}
User Satisfaction: {random.choice(['5/5 — Resolved quickly','4/5 — Good service','5/5 — Very helpful','Not rated','3/5 — Took longer than expected'])}
"""
    return maybe_typo(content)


def gen_asset_record():
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    asset_types = [
        ("Laptop","Dell Latitude 5540","Workstation"),
        ("Desktop","HP EliteDesk 800 G9","Workstation"),
        ("Laptop","Lenovo ThinkPad T14","Workstation"),
        ("Printer","HP LaserJet Pro M404","Printer"),
        ("Desktop","Dell OptiPlex 7010","Workstation"),
        ("Tablet","Microsoft Surface Pro 9","Mobile"),
        ("Laptop","Apple MacBook Pro 14","Workstation"),
    ]
    atype, model, category = random.choice(asset_types)
    emp = rname()
    content = f"""{org}
IT ASSET INVENTORY RECORD
Asset ID: ASSET-{random.randint(10000,99999)}
Record Date: {dt.strftime('%m/%d/%Y')}

DEVICE INFORMATION
Asset Type: {atype}
Manufacturer/Model: {model}
Serial Number: {rserial()}
MAC Address (Primary): {rmac()}
MAC Address (WiFi): {rmac()}
Category: {category}
OS: {random.choice(['Windows 11 Pro','Windows 10 Pro','macOS Ventura','Windows 11 Enterprise'])}
OS Version: {random.choice(['22H2','23H2','21H2','Ventura 13.4'])}
Processor: {random.choice(['Intel Core i5-1345U','Intel Core i7-1265U','AMD Ryzen 5 PRO 7540U','Apple M2 Pro'])}
RAM: {random.choice(['8 GB','16 GB','32 GB'])}
Storage: {random.choice(['256 GB SSD','512 GB SSD','1 TB SSD'])}

ASSIGNMENT
Assigned To: {emp}
Employee ID: {rempid()}
Department: {random.choice(DEPARTMENTS)}
Location: {random.choice(['Building A','Building B — Clinic','Remote','IT Storage','Lab Wing'])}
Date Assigned: {dt.strftime('%m/%d/%Y')}
Purpose: {random.choice(['Primary Workstation','Shared Workstation','Lab System','Mobile Clinical Device','Loaner'])}

WARRANTY & SUPPORT
Purchase Date: {rdate(dt.year-2, dt.year).strftime('%m/%d/%Y')}
Warranty Expiry: {rdate(dt.year, dt.year+3).strftime('%m/%d/%Y')}
Support Contract: {random.choice(['Dell ProSupport Plus','HP Care Pack','AppleCare+','None'])}
Last Maintenance: {rdate(dt.year-1, dt.year).strftime('%m/%d/%Y')}

SECURITY
BitLocker/FileVault: {random.choice(['Enabled','Enabled','Enabled','Not Configured — REMEDIATE'])}
Antivirus: {random.choice(['CrowdStrike Falcon','Defender + Sentinel One','CrowdStrike Falcon'])}
Last Patch Date: {rdate(dt.year, 2026).strftime('%m/%d/%Y')}
Encryption Key Escrowed: {random.choice(['Yes','Yes','Yes','No'])}
"""
    return content


def gen_server_record():
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    server_roles = [
        ("DC-01","Domain Controller","Windows Server 2022","Active Directory, DNS, DHCP"),
        ("FS-01","File Server","Windows Server 2019","Shared storage, DFS Namespace"),
        ("APP-EHR-01","EHR Application Server","Windows Server 2022","NovaMed EHR Application Tier"),
        ("DB-01","Database Server","Windows Server 2022 + SQL Server 2022","EHR Database, Clinical Data"),
        ("MAIL-01","Email Server","Windows Server 2019","Exchange Hybrid"),
        ("BACKUP-01","Backup Server","Windows Server 2022","Veeam Backup & Replication"),
        ("VPN-01","VPN Gateway","pfSense 2.7","Remote Access VPN"),
        ("WSUS-01","Patch Management","Windows Server 2019","WSUS + Patch Management"),
    ]
    hostname, role, os_name, services = random.choice(server_roles)
    content = f"""{org}
IT ASSET — SERVER RECORD
Hostname: {hostname}
Asset ID: SRV-{random.randint(1000,9999)}
Record Updated: {dt.strftime('%m/%d/%Y')}

HARDWARE
Manufacturer: {random.choice(['Dell PowerEdge R750','HPE ProLiant DL380 Gen10','Dell PowerEdge R640'])}
Serial Number: {rserial()}
Role: {role}
Location: Server Room — {random.choice(['Rack A','Rack B','Rack C'])} U{random.randint(1,42)}

SOFTWARE
Operating System: {os_name}
Services Hosted: {services}
IP Address: 10.{random.randint(1,10)}.{random.randint(1,10)}.{random.randint(10,250)}
Subnet: 255.255.255.0

MAINTENANCE
Last Patched: {rdate(dt.year, 2026).strftime('%m/%d/%Y')}
Last Backup: {(datetime.now() - timedelta(days=random.randint(0,3))).strftime('%m/%d/%Y')}
Backup Status: {random.choice(['Success','Success','Success','Failed — investigate'])}
Uptime: {random.randint(1,365)} days
Monitored by: {random.choice(['Zabbix','PRTG','SolarWinds','ManageEngine'])}

CONTACTS
Primary Admin: {rname()}
Backup Admin: {rname()}
Vendor Support: {random.choice(VENDORS)}
"""
    return content


def gen_security_incident():
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    incident_types = [
        ("PHI-001","Potential PHI Exposure",
         "Employee reported receiving an email containing what appeared to be patient data from an external, non-organizational sender. Email was quarantined.",
         "MEDIUM","Email quarantined, user interviewed, no confirmed breach. Monitoring ongoing."),
        ("PHISH-001","Phishing Attempt — Credential Harvesting",
         "Simulated phishing email deployed as part of awareness training. 12 users clicked the link. 3 submitted credentials.",
         "HIGH","Affected users received immediate targeted training. Credentials reset. Report sent to CISO."),
        ("MALWARE-001","Malware Detection on Endpoint",
         "CrowdStrike Falcon detected and quarantined a trojan on workstation ASSET-48291 assigned to a billing department employee.",
         "HIGH","Endpoint isolated. Forensic image taken. Drive wiped and reimaged. User account audited. No lateral movement detected."),
        ("UNAUTH-001","Unauthorized Access Attempt",
         "EHR audit logs detected after-hours access attempts from user account belonging to a recently terminated employee.",
         "CRITICAL","Account was disabled at termination but PAM exception overlooked. Access revoked. Offboarding checklist updated."),
        ("USB-001","Unauthorized USB Device Detected",
         "DLP tool flagged a non-approved USB storage device connected to a nursing station workstation. Device was personal.",
         "LOW","User counseled. Device removed. USB policy reminder sent to department."),
    ]
    inc_id_prefix, inc_type, desc, severity, resolution = random.choice(incident_types)
    inc_id = f"SEC-{dt.year}-{random.randint(1000,9999)}"
    content = f"""{org}
SECURITY INCIDENT REPORT
Incident ID: {inc_id}
Date Reported: {dt.strftime('%m/%d/%Y')}
Reported by: {rname()}
Type: {inc_type}
Severity: {severity}

DESCRIPTION
{desc}

AFFECTED SYSTEMS / USERS
{random.choice(['Workstation ASSET-'+str(random.randint(10000,99999)),'User account: '+remail(rname()),'Nursing Station 3E — shared terminal','Multiple email accounts','EHR system access logs'])}

TIMELINE
{dt.strftime('%m/%d/%Y')} {random.randint(7,12):02d}:{random.randint(0,59):02d} — Incident detected/reported
{dt.strftime('%m/%d/%Y')} {random.randint(12,16):02d}:{random.randint(0,59):02d} — Security team notified
{(dt + timedelta(days=1)).strftime('%m/%d/%Y')} — Initial investigation completed
{(dt + timedelta(days=random.randint(2,7))).strftime('%m/%d/%Y')} — Remediation completed

RESOLUTION
{resolution}

BREACH DETERMINATION
Confirmed PHI Breach: {random.choice(['No','No','No','Yes — reported to Privacy Officer'])}
OCR Notification Required: {random.choice(['No','No','No','Yes — within 60 days'])}
Patient Notification Required: {random.choice(['No','No','Pending legal review'])}

Investigated by: {rname()} — Information Security
Reviewed by: {random.choice(MANAGERS)} — CISO
"""
    return content


def gen_vulnerability_scan():
    dt = rdate(2018, 2026)
    org = get_org(dt.year)
    scanner = random.choice(["Tenable Nessus","Qualys VMDR","Rapid7 InsightVM"])
    hosts_scanned = random.randint(50, 400)
    critical = random.randint(0, 8)
    high = random.randint(0, 25)
    medium = random.randint(5, 60)
    low = random.randint(10, 120)
    content = f"""{org}
VULNERABILITY SCAN REPORT
Scan Date: {dt.strftime('%m/%d/%Y')}
Scanner: {scanner}
Scan Type: {random.choice(['Authenticated Internal Scan','Unauthenticated External Scan','PCI ASV Scan','Full Network Discovery'])}
Scope: {random.choice(['All internal endpoints','Clinical network segment','Administrative network','DMZ and public-facing servers'])}

EXECUTIVE SUMMARY
Hosts Scanned: {hosts_scanned}
Hosts with Vulnerabilities: {random.randint(hosts_scanned//3, hosts_scanned)}
Scan Duration: {random.randint(45,360)} minutes

FINDINGS SUMMARY
  Critical (CVSS 9.0-10.0): {critical}
  High     (CVSS 7.0-8.9):  {high}
  Medium   (CVSS 4.0-6.9):  {medium}
  Low      (CVSS 0.1-3.9):  {low}
  Informational:             {random.randint(20,200)}

TOP CRITICAL/HIGH FINDINGS
"""
    vulns = [
        ("CVE-2021-44228","Apache Log4j Remote Code Execution","10.0","Patch to Log4j 2.17.1+"),
        ("CVE-2023-23397","Microsoft Outlook Privilege Escalation","9.8","Apply MS Patch KB5023706"),
        ("CVE-2022-26134","Confluence Server RCE","9.8","Upgrade to Confluence 7.4.17"),
        ("CVE-2021-34527","Windows Print Spooler RCE (PrintNightmare)","8.8","Disable Print Spooler on non-print servers"),
        ("CVE-2020-0796","SMBv3 RCE (SMBGhost)","10.0","Apply KB4551762"),
        ("CVE-2019-11510","Pulse Secure VPN Path Traversal","10.0","Upgrade to Pulse Connect Secure 9.1R3"),
        ("Weak SSL/TLS Configuration","TLS 1.0/1.1 enabled on web server","5.3","Disable TLS 1.0 and 1.1"),
        ("Default Credentials","Network device with default admin credentials","9.1","Change credentials per policy"),
    ]
    for v in random.sample(vulns, min(4, critical+high)):
        cve, title, cvss, remediation = v
        content += f"  [{cve}] {title} — CVSS {cvss}\n    Remediation: {remediation}\n\n"

    content += f"""
REMEDIATION STATUS (from prior scan)
  Items remediated since last scan: {random.randint(5,40)}
  Items past due (>90 days): {random.randint(0,12)}

Next Scan Scheduled: {(dt + timedelta(days=90)).strftime('%m/%d/%Y')}
Report Prepared by: {rname()}, Security Analyst
Reviewed by: {random.choice(MANAGERS)}, CISO
"""
    return content


def gen_change_request():
    dt = rdate(2017, 2026)
    org = get_org(dt.year)
    chg_id = f"CHG-{dt.year}-{random.randint(1000,9999)}"
    changes = [
        ("Firewall Rule Update","Add allow rule for new EHR module communication between APP-EHR-01 and DB-01 on TCP 1433.","Low","Standard"),
        ("Server OS Patching","Apply July 2024 Microsoft Patch Tuesday updates to all production servers.",
         "Medium","Standard"),
        ("Active Directory Group Policy Update","Update GPO to enforce 90-day password policy and enforce MFA for all VPN users.","Low","Normal"),
        ("Network Switch Replacement","Replace aging Cisco Catalyst 2960 switches in Building B with Catalyst 9200L.",
         "High","Normal"),
        ("EHR Upgrade","Upgrade NovaMed EHR from version 4.1 to 4.3. Scheduled downtime required.","High","Major"),
        ("SSL Certificate Renewal","Renew wildcard SSL certificate for *.northstar-health.internal expiring in 30 days.","Medium","Emergency"),
        ("New VPN Client Deployment","Push updated GlobalProtect VPN client v6.2 to all endpoints via SCCM.","Low","Standard"),
    ]
    title, desc, risk, chg_type = random.choice(changes)
    impl_date = dt + timedelta(days=random.randint(7, 21))
    content = f"""{org}
CHANGE MANAGEMENT REQUEST
Change ID: {chg_id}
Date Submitted: {dt.strftime('%m/%d/%Y')}
Requested by: {rname()}
Department: {random.choice(['Information Technology','Network Engineering','Clinical Informatics'])}

CHANGE TITLE: {title}
Change Type: {chg_type}
Risk Level: {risk}
Urgency: {random.choice(['Low','Medium','High'])}
Status: {random.choice(['Approved','Pending CAB Review','Approved','Rejected','Implemented'])}

DESCRIPTION
{desc}

BUSINESS JUSTIFICATION
{random.choice([
    'Required for regulatory compliance and security posture improvement.',
    'Necessary to support clinical operations and EHR functionality.',
    'Vendor end-of-support deadline approaching. Upgrade required to maintain support.',
    'Security vulnerability remediation — critical priority.',
    'Operational efficiency improvement requested by department leadership.',
])}

IMPLEMENTATION PLAN
Planned Start: {impl_date.strftime('%m/%d/%Y')} {random.choice(['06:00','22:00','02:00'])} (off-hours)
Planned End: {impl_date.strftime('%m/%d/%Y')} {random.choice(['08:00','06:00','04:00'])}
Maintenance Window: Approved maintenance window
Lead Implementer: {rname()}
Backup Contact: {rname()}

ROLLBACK PLAN
{random.choice([
    'Restore from pre-change snapshot taken 30 minutes prior to implementation.',
    'Revert firewall rule and test connectivity.',
    'Reinstall previous EHR version from backup media.',
    'Restore previous GPO from backup.',
])}

CAB Approval: {random.choice(MANAGERS)}
Date Approved: {dt.strftime('%m/%d/%Y')}
"""
    return content


def generate_it_documents():
    generated = 0

    for i in range(150):
        dt = rdate(2016, 2026)
        status = "Open" if random.random() < 0.2 else "Closed"
        subdir = f"IT/Tickets/{'Open' if status=='Open' else 'Closed'}"
        ticket_id = f"INC{random.randint(10000,99999)}"
        fname = f"ticket_{ticket_id}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / subdir / fname, gen_help_desk_ticket())
        tick("IT-Ticket"); generated += 1

    for i in range(80):
        dt = rdate(2016, 2026)
        fname = f"asset_endpoint_{rserial()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / "IT/Assets/Endpoints" / fname, gen_asset_record())
        tick("IT-Asset"); generated += 1

    for i in range(30):
        dt = rdate(2016, 2026)
        fname = f"server_record_{rserial()}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / "IT/Assets/Servers" / fname, gen_server_record())
        tick("IT-Srv"); generated += 1

    for i in range(60):
        dt = rdate(2016, 2026)
        fname = f"security_incident_SEC{dt.year}{random.randint(1000,9999)}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / "IT/Security/Incidents" / fname, gen_security_incident())
        tick("IT-SecInc"); generated += 1

    for i in range(30):
        dt = rdate(2018, 2026)
        fname = f"vuln_scan_{dt.strftime('%Y%m%d')}_report.txt"
        write_file(BASE / "IT/Security/Vulnerability" / fname, gen_vulnerability_scan())
        tick("IT-Vuln"); generated += 1

    for i in range(50):
        dt = rdate(2017, 2026)
        fname = f"change_request_CHG{dt.year}{random.randint(1000,9999)}_{dt.strftime('%Y%m%d')}.txt"
        write_file(BASE / "IT/ChangeManagement" / fname, gen_change_request())
        tick("IT-CHG"); generated += 1

    return generated

print("Starting IT document generation...")
it_count = generate_it_documents()
print(f"IT documents done: {it_count}")

# ─── EXECUTIVE DOCUMENT GENERATORS ───────────────────────────────────────────

def gen_board_minutes():
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    quarter = (dt.month - 1) // 3 + 1
    board_members = [rname() for _ in range(random.randint(7, 11))]
    chair = board_members[0]
    agenda_items = random.sample([
        "Review of Q{} Financial Statements".format(quarter),
        "Chief Medical Officer Report",
        "Chief Nursing Officer Report",
        "HIPAA Compliance Update",
        "Capital Expenditure Approval — {}" .format(random.choice(["New MRI Suite","Building Renovation","IT Infrastructure Upgrade","EHR Expansion"])),
        "Medical Staff Credentialing Report",
        "Quality Metrics Dashboard Review",
        "Strategic Plan Progress Update",
        "Cybersecurity Posture Briefing",
        "Vendor Contract Approval",
        "Policy Revisions — First Reading",
        "Community Benefit Report",
        "CEO Performance Review",
    ], k=random.randint(4,7))
    votes = [(item, random.choice(["Approved unanimously","Approved {}-{}".format(len(board_members)-1,1),"Tabled for further review","Referred to Finance Committee"])) for item in agenda_items if "Approval" in item or "Revisions" in item or "Contract" in item]
    content = f"""{org}
BOARD OF DIRECTORS MEETING MINUTES
{random.choice(['Regular Session','Special Session'])} — Q{quarter} {dt.year}
Date: {dt.strftime('%B %d, %Y')}
Location: {random.choice(['Main Conference Room, Building A, Suite 400','Teleconference (Zoom)','Executive Board Room, Administration Wing'])}
Meeting Called to Order: {random.randint(8,10):02d}:{random.choice(['00','15','30'])} AM
Chair: {chair}

BOARD MEMBERS PRESENT
{chr(10).join(f'  - {m}' for m in board_members)}

BOARD MEMBERS ABSENT
  - {rname()} (excused)

AGENDA & DISCUSSION
"""
    for i, item in enumerate(agenda_items, 1):
        content += f"\n{i}. {item}\n"
        content += f"   {random.choice(['Discussion ensued. No action required at this time.','Presentation provided by staff. Board members asked clarifying questions.','Report accepted as presented.','Detailed briefing provided. Follow-up requested for next meeting.'])}\n"

    if votes:
        content += "\nVOTING RECORD\n"
        for item, outcome in votes:
            content += f"  MOTION: {item} — {outcome}\n"

    content += f"""
NEXT MEETING: {(dt + timedelta(days=90)).strftime('%B %d, %Y')}
Meeting Adjourned: {random.randint(10,13):02d}:{random.choice(['00','15','30','45'])} AM

Respectfully submitted,
{rname()}
Board Secretary
"""
    return content


def gen_budget_report():
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    depts = random.sample(DEPARTMENTS, random.randint(5,10))
    content = f"""{org}
DEPARTMENTAL BUDGET REPORT
Fiscal Year: {dt.year}
Period: {random.choice(['Q1','Q2','Q3','Q4','Annual'])} {dt.year}
Prepared by: {random.choice(MANAGERS)}, Finance
Date: {dt.strftime('%m/%d/%Y')}

SUMMARY
{'Department':<30} {'Budget':>15} {'Actual':>15} {'Variance':>12} {'%Var':>8}
{'-'*85}
"""
    total_budget = 0
    total_actual = 0
    for dept in depts:
        budget = random.randint(200, 4000) * 1000
        variance_pct = random.uniform(-0.12, 0.08)
        actual = int(budget * (1 + variance_pct))
        variance = actual - budget
        total_budget += budget
        total_actual += actual
        flag = " **" if variance_pct > 0.05 else ""
        content += f"{dept:<30} ${budget:>13,} ${actual:>13,} ${variance:>10,}{'+' if variance > 0 else ''} {variance_pct*100:>6.1f}%{flag}\n"

    total_var = total_actual - total_budget
    content += f"""
{'-'*85}
{'TOTAL':<30} ${total_budget:>13,} ${total_actual:>13,} ${total_var:>10,} {(total_var/total_budget*100):>6.1f}%

** Exceeds budget threshold — department head notified

KEY VARIANCES EXPLAINED
{random.choice([
    'Nursing overtime costs increased due to increased patient volume and temporary staffing gaps.',
    'IT capital expenditures exceeded budget following emergency EHR server replacement.',
    'Pharmacy costs favorable due to successful generic drug substitution program.',
    'HR savings attributed to delayed backfill hiring for open positions.',
])}

CFO Notes: {random.choice([
    'Overall performance within acceptable parameters. Q3 outlook remains stable.',
    'Finance committee to review overtime trends with department managers.',
    'Capital expenditure request for next fiscal year due by October 1.',
    'Year-end projections updated. Board reporting package in preparation.',
])}
"""
    return content


def gen_vendor_contract():
    dt = rdate(2016, 2026)
    org = get_org(dt.year)
    vendor = random.choice(VENDORS)
    contract_types = [
        "Software License and Support Agreement",
        "Professional Services Agreement",
        "Business Associate Agreement (HIPAA)",
        "Equipment Maintenance and Service Contract",
        "Staffing Agency Master Services Agreement",
        "Medical Supply Distribution Agreement",
    ]
    term_years = random.randint(1, 5)
    value = random.randint(25, 2000) * 1000
    content = f"""{org}
CONTRACT SUMMARY SHEET
Contract ID: CTR-{dt.year}-{random.randint(1000,9999)}
Contract Type: {random.choice(contract_types)}
Date Executed: {dt.strftime('%m/%d/%Y')}

PARTIES
Organization: {org}
Vendor/Counterparty: {vendor}
Vendor Contact: {rname()}
Vendor Address: {raddress()}
Vendor Phone: {rphone()}

CONTRACT TERMS
Effective Date: {dt.strftime('%m/%d/%Y')}
Expiration Date: {datetime(dt.year + term_years, dt.month, dt.day).strftime('%m/%d/%Y')}
Term Length: {term_years} year(s)
Auto-Renewal: {random.choice(['Yes — 30-day notice to cancel','No','Yes — 60-day notice to cancel'])}
Total Contract Value: ${value:,}
Payment Terms: {random.choice(['Net 30','Net 45','Monthly','Quarterly','Annually in advance'])}

SCOPE OF SERVICES
{random.choice([
    f'Provision of {random.choice(["medical supplies","software licenses","staffing services","IT hardware","training services"])} as detailed in Exhibit A.',
    f'Vendor will provide {random.choice(["maintenance and support","consulting services","managed services","SaaS platform access"])} per specifications in attached SOW.',
    f'Services include {random.choice(["24/7 technical support","on-site maintenance","staff augmentation","training and implementation services"])}.',
])}

HIPAA BAA: {random.choice(['Included as Exhibit C','Executed separately — on file','Not required — no PHI access'])}
Insurance Required: ${random.randint(1,5)}M General Liability, ${random.randint(1,5)}M Professional Liability

KEY CONTACTS
Internal Owner: {random.choice(MANAGERS)}
Legal Review by: {rname()}, General Counsel
Procurement: {rname()}
"""
    return content


def gen_risk_assessment():
    dt = rdate(2018, 2026)
    org = get_org(dt.year)
    risks = [
        ("Ransomware Attack on Clinical Systems","Cybersecurity","Critical","High","MED","Deploy EDR, enforce MFA, maintain offline backups, conduct tabletop exercises quarterly."),
        ("Unplanned EHR Downtime","IT / Clinical Operations","High","Medium","LOW","Implement downtime procedures, test failover quarterly, maintain paper downtime forms."),
        ("HIPAA Privacy Breach","Compliance","High","Medium","MED","Annual training, access audits, DLP controls, incident response plan."),
        ("Staff Shortage — Nursing","Workforce","High","High","HIGH","PRN pool expansion, agency contracts, competitive compensation review."),
        ("Medical Device Vulnerability","Cybersecurity / Patient Safety","Critical","Low","LOW","Device inventory, network segmentation, vendor patch coordination."),
        ("Regulatory Audit Finding","Compliance","Medium","Medium","MED","Mock audit program, policy review calendar, documentation standards."),
        ("Vendor Business Continuity Failure","Operations","Medium","Low","LOW","Dual-vendor strategy for critical supplies, contract SLAs with penalties."),
    ]
    selected = random.sample(risks, random.randint(4, len(risks)))
    content = f"""{org}
ENTERPRISE RISK ASSESSMENT
Assessment Date: {dt.strftime('%m/%d/%Y')}
Prepared by: {random.choice(MANAGERS)}
Reviewed by: {random.choice(MANAGERS)}, Chief Risk Officer

RISK REGISTER
{'Risk':<45} {'Category':<25} {'Severity':<10} {'Likelihood':<12} {'Residual':<10}
{'-'*110}
"""
    for risk, cat, sev, like, resid, mitigation in selected:
        content += f"{risk:<45} {cat:<25} {sev:<10} {like:<12} {resid:<10}\n"

    content += "\nMITIGATION DETAILS\n"
    for risk, cat, sev, like, resid, mitigation in selected:
        content += f"\n  [{cat}] {risk}\n  Mitigation: {mitigation}\n"

    content += f"""
OVERALL RISK POSTURE: {random.choice(['MODERATE','MODERATE','ELEVATED','ACCEPTABLE'])}
Next Review: {(dt + timedelta(days=180)).strftime('%m/%d/%Y')}
"""
    return content


def generate_executive_documents():
    generated = 0

    for yr in range(2016, 2027):
        for q in range(1, 5):
            if yr == 2026 and q > 2:
                break
            fname = f"board_minutes_Q{q}_{yr}.txt"
            write_file(BASE / "Executive/BoardMeetings" / fname, gen_board_minutes())
            tick("Exec-Board"); generated += 1

    for yr in range(2016, 2027):
        for q in range(1, 5):
            if yr == 2026 and q > 2:
                break
            fname = f"budget_report_Q{q}_{yr}.txt"
            write_file(BASE / "Executive/Budget" / fname, gen_budget_report())
            tick("Exec-Budget"); generated += 1

    for i in range(40):
        dt = rdate(2016, 2026)
        fname = f"vendor_contract_{random.choice(VENDORS).replace(' ','_').replace('.','').replace(',','')}_{dt.year}_{random.randint(1000,9999)}.txt"
        subdir = random.choice(["Legal/Contracts","Legal/Vendor"])
        write_file(BASE / subdir / fname, gen_vendor_contract())
        tick("Exec-Contract"); generated += 1

    for i in range(20):
        dt = rdate(2018, 2026)
        fname = f"risk_assessment_{dt.strftime('%Y%m%d')}.txt"
        subdir = random.choice(["Executive/Strategy","Compliance/Audits"])
        write_file(BASE / subdir / fname, gen_risk_assessment())
        tick("Exec-Risk"); generated += 1

    for i in range(30):
        dt = rdate(2016, 2026)
        org = get_org(dt.year)
        fname = f"qbr_{dt.year}_Q{(dt.month-1)//3+1}.txt"
        qbr_content = f"""{org}
QUARTERLY BUSINESS REVIEW
Period: Q{(dt.month-1)//3+1} {dt.year}
Date: {dt.strftime('%m/%d/%Y')}
Presented by: {random.choice(MANAGERS)}

KEY METRICS
Patient Volume: {random.randint(8000,25000):,} visits
Revenue: ${random.randint(4,15) * 1000000:,}
Operating Margin: {round(random.uniform(2.1, 12.5), 1)}%
Patient Satisfaction (HCAHPS): {round(random.uniform(78.0, 96.0), 1)}%
Employee Turnover: {round(random.uniform(8.0, 22.0), 1)}%
Days in AR: {random.randint(38, 68)}
Denial Rate: {round(random.uniform(3.5, 12.0), 1)}%

HIGHLIGHTS
- {random.choice(['Successful EHR go-live completed on schedule.','New outpatient clinic opened in Lakedale.','Patient satisfaction scores improved 4 points YoY.','Achieved Joint Commission accreditation renewal.','Launched telehealth program serving 1,200 new patients.'])}

CHALLENGES
- {random.choice(['Continued nursing staffing shortages in ED.','Denials from BluePeak Health Partners increased 8%.','Supply chain disruptions impacting surgical inventory.','IT infrastructure upgrade behind schedule.','COVID-related volume fluctuations continue to impact planning.'])}

Next QBR: {(dt + timedelta(days=90)).strftime('%B %d, %Y')}
"""
        write_file(BASE / "Executive/Strategy" / fname, qbr_content)
        tick("Exec-QBR"); generated += 1

    for i in range(20):
        dt = rdate(2019, 2026)
        org = get_org(dt.year)
        fname = f"hipaa_compliance_report_{dt.year}_{random.randint(100,999)}.txt"
        content = f"""{org}
HIPAA COMPLIANCE STATUS REPORT
Date: {dt.strftime('%m/%d/%Y')}
Prepared by: {random.choice(MANAGERS)}, Privacy Officer

PRIVACY RULE COMPLIANCE
Notices of Privacy Practices: {random.choice(['Current and posted','Updated — effective March 2024','Under revision'])}
Patient Rights Requests (YTD): {random.randint(5,80)}
  - Access Requests: {random.randint(3,50)}
  - Amendment Requests: {random.randint(0,10)}
  - Accounting of Disclosures: {random.randint(0,5)}
Complaints Received: {random.randint(0,6)}
Complaints Resolved: {random.randint(0,6)}

SECURITY RULE COMPLIANCE
Annual Risk Analysis: {random.choice(['Completed','In Progress','Scheduled Q4'])}
Security Awareness Training Completion: {random.randint(82,100)}%
Workforce Members Trained: {random.randint(2000,2500):,} / 2,500
Business Associate Agreements Active: {random.randint(40,90)}
Breaches Reported to OCR (YTD): {random.randint(0,2)}

BREACH LOG
{random.choice(['No reportable breaches this period.','1 reportable breach — misdirected fax, 2 patients affected, notified.','No breaches meeting notification threshold.'])}

Compliance Status: {random.choice(['COMPLIANT','COMPLIANT','MONITORING REQUIRED — see attached'])}
"""
        write_file(BASE / "Compliance/HIPAA" / fname, content)
        tick("Exec-HIPAA"); generated += 1

    return generated

print("Starting executive document generation...")
exec_count = generate_executive_documents()
print(f"Executive documents done: {exec_count}")

# ─── PERSONAL / CLUTTER DOCUMENT GENERATORS ──────────────────────────────────

JOURNAL_EMPLOYEES = [
    ("Brianna Castellano", "Nursing", "3-East floor, charge nurse on Tuesdays"),
    ("Darnell Hubbard", "IT", "help desk, sits near the printer that always jams"),
    ("Marisol Espinoza", "Billing", "works early shift, car pool with Marcus"),
    ("Fletcher Radford", "Administration", "coordinator, planning a kitchen remodel"),
    ("Latasha Okonkwo", "HR", "generalist, training for a 5K"),
    ("Ivan Kowalski", "Security", "night shift officer, listens to podcasts"),
    ("Simone Garland", "Pharmacy", "floats between campuses, loves true crime"),
    ("Kaden Abernathy", "Laboratory", "lab tech, annoyed about the parking situation"),
    ("Ophelia Santiago", "Physical Therapy", "PT, planning Hawaii trip for anniversary"),
    ("Nelson Merriweather", "Radiology", "rad tech, into fantasy football"),
    ("Colette Lavoie", "Executive", "assistant to the CMO, keeps everything running"),
    ("Jamison Tanner", "Housekeeping", "evening shift, big family, saving for new truck"),
    ("Fatima Adeyemi", "Compliance", "loves her book club, dreads audit season"),
    ("Leandro Vasquez", "Surgery", "surgical tech, just bought a house"),
    ("Evangeline Whitmore", "Pediatrics", "pediatric nurse, three cats, avid baker"),
]

JOURNAL_TOPICS = [
    lambda name, dept: f"Long day. We were short two nurses on the {dept} floor again. {rname()} picked up an extra shift but honestly nobody should have to do that every week. My feet are killing me. Made pasta when I got home, watched TV, fell asleep on the couch.",
    lambda name, dept: f"Had my 1-on-1 with my manager today. {random.choice(MANAGERS)} actually said something nice about my documentation which I was not expecting. Maybe things are turning around. Still annoyed about the parking lot situation — I circled for 20 minutes.",
    lambda name, dept: f"The new {get_ehr(random.randint(2016,2026))} training was today. Three hours. It was fine I guess, some of it was actually useful. The interface is better than the old system. {rname()} keeps complaining about it but I think they just don't like change.",
    lambda name, dept: f"Grocery list for the week:\n- chicken thighs\n- broccoli\n- greek yogurt\n- coffee (the good kind)\n- bananas\n- pasta\n- canned tomatoes\n- shredded cheese\n- bread\n- sparkling water\nAlso need to pick up a birthday card for mom.",
    lambda name, dept: f"Thinking about the vacation to {random.choice(['Sedona','Portland','New Orleans','Charleston SC','Colorado Springs','Savannah'])}. Looked at flights — {random.choice(['pretty reasonable','kind of expensive','there was a deal for $189 roundtrip I should probably grab'])}. Need to figure out if I can get the time off approved. {random.choice(['Asked my manager already.','Have not asked yet.','Already submitted the PTO request.'])}",
    lambda name, dept: f"Someone AGAIN took my yogurt from the break room fridge. I labeled it. There is a sticky note with my name on it. I am not imagining things. Going to say something at the next staff meeting.",
    lambda name, dept: f"Gym update: {random.choice(['Hit a new PR on the bench press today. 185 lbs. Been working on it for months.','Skipped again. Work was too long. Going tomorrow for sure.','Ran 4 miles this morning before my shift. Felt amazing until about 2pm.','Signed up for a yoga class on Saturdays. We will see.'])}",
    lambda name, dept: f"Recipe I tried this weekend:\n\nButter Chicken (pretty good version)\n- 2 lbs chicken thighs, cubed\n- 1 can crushed tomatoes\n- 1 cup cream\n- 2 tsp garam masala\n- 1 tsp turmeric\n- 1 tsp cumin\n- 2 cloves garlic\n- 1 inch fresh ginger\nCook chicken, make sauce, combine. Serve over basmati rice. {rname()} said it was the best thing I've ever made which is saying something.",
    lambda name, dept: f"The copier on the second floor is broken AGAIN. Filed a ticket — INC-{random.randint(10000,99999)}. {rname()} from IT says it's a known issue with the drum. They've ordered parts. In the meantime we have to walk all the way to Building B to print anything. Annoying.",
    lambda name, dept: f"Budget meeting ran an hour over. The usual. {random.choice(MANAGERS)} kept going back to the variance on the staffing line which is fair but we've been over that three times now. At least there were snacks.",
    lambda name, dept: f"Kid stuff today: {random.choice(['Soccer tournament all day Saturday. My kid scored twice.','Parent-teacher conference — mostly good news. Teacher says they need to work on math.','School play rehearsal pickup at 6pm. Rush from work to get there. Made it with 2 minutes to spare.','Science fair project is due Friday. We are not prepared.'])}",
    lambda name, dept: f"Something kind of funny happened today. {rname()} walked into the wrong meeting — just confidently sat down before realizing the room was full of people they didn't know. We were all very polite about it. It broke the ice at least.",
    lambda name, dept: f"End of the week. Things I am grateful for:\n1. Nobody coded today\n2. The vending machine had the good chips\n3. Found a parking spot near the entrance for once\n4. Only {random.randint(3,18)} unread emails tonight\n5. Weekend is almost here",
    lambda name, dept: f"Annual review next week. Nervous even though I know my performance has been solid. I hate these things. {random.choice(['My manager is fine but I never know what they are really thinking.','I think it will go well. I documented everything this year.','Just want it to be over honestly.'])}",
    lambda name, dept: f"Overheard someone in the hallway talking about layoffs. Probably rumors but you never know. I have been here {random.randint(2,12)} years and I would like to stay. Going to make sure my work is visible this quarter.",
]


def gen_journal_entry(employee, dept, description):
    dt = rdate(2016, 2026)
    topic_fn = random.choice(JOURNAL_TOPICS)
    body = topic_fn(employee, dept)
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    content = f"""--- Personal Journal ---
{dt.strftime('%A, %B %d, %Y')}

{body}

-- {employee.split()[0]}
"""
    return content


def gen_humor_file(fname_hint):
    if "chili" in fname_hint:
        entries = [(rname(), random.randint(1,12), random.choice(["Too spicy but in a good way","Legitimately the best one","Needs more beans","Very authentic, what does that mean","TOO SWEET this is not chili","People were going back for thirds","Surprised how much I liked it","The cornbread pairing was inspired"])) for _ in range(random.randint(8,14))]
        content = "NorthStar Regional Health Network\n2nd Annual Breakroom Chili Cook-Off Rankings\n"
        content += f"Event Date: {rdate(2018,2024).strftime('%B %d, %Y')}\n\n"
        content += f"{'Rank':<6}{'Contestant':<30}{'Score /10':<12}{'Judge Comments'}\n"
        content += "-"*80 + "\n"
        ranked = sorted(entries, key=lambda x: -x[1])
        for i, (name, score, comment) in enumerate(ranked, 1):
            content += f"{i:<6}{name:<30}{score:<12}{comment}\n"
        content += f"\nWINNER: {ranked[0][0]} — Congratulations!\nTotal participants: {len(entries)}\nPrize: $20 gift card to Hartmoor Bistro\n"
        return content

    elif "fantasy_football" in fname_hint:
        players = [(rname(), random.randint(80,160), random.randint(0,14), random.randint(0,14)) for _ in range(10)]
        ranked = sorted(players, key=lambda x: -x[1])
        content = f"NorthStar Regional Health Network\nOfficial Fantasy Football League {random.randint(2019,2024)}\nFinal Standings\n\n"
        content += f"{'Place':<8}{'Manager':<30}{'Points':<10}{'W':<6}{'L'}\n"
        content += "-"*60+"\n"
        for i, (name, pts, w, l) in enumerate(ranked, 1):
            content += f"{i:<8}{name:<30}{pts:<10}{w:<6}{l}\n"
        content += f"\n2024 League Champion: {ranked[0][0]}\nLast Place (Sacko Trophy): {ranked[-1][0]}\n"
        return content

    elif "yogurt" in fname_hint:
        suspects = [rname() for _ in range(3)]
        content = """RE: Ongoing Situation With the Fridge

I have been meaning to write this down because I am losing my mind.

For the THIRD TIME this month someone has taken my yogurt. Greek yogurt. Strawberry. 
Labeled with my name and the date. It is not ambiguous.

Suspects based on who is in early:
"""
        for s in suspects:
            content += f"  - {s} (arrives around 7am, often in break room)\n"
        content += f"""
I am not accusing anyone. I am just saying.

I bought a small cooler bag. Going forward my yogurt will be at my desk.
This is not sustainable as an organization if we cannot respect clearly labeled items.

Sent to: shared_breakroom_concerns@northstarhealth.local (and nobody responded, of course)

— {rname()}
"""
        return content

    elif "coffee" in fname_hint:
        complaints = [
            f"{rname()}: Who is making half a pot and not making more? This is chaos.",
            f"{rname()}: The coffee was COLD at 9am. Who made it? When?",
            f"{rname()}: If you use the last of the creamer please replace it. It's in the cabinet above the sink.",
            f"{rname()}: Decaf is not 'also coffee' it should not be in the regular pot spot.",
            f"{rname()}: I found a mug in the pot. A full mug. In the coffee pot.",
            f"{rname()}: Please wash your mugs. The sink situation is out of control.",
            f"{rname()}: Someone put sweet and low in the coffee canister. I found out the hard way.",
            f"{rname()}: This coffee tastes like burnt regret. Whoever sets the heat plate to max — PLEASE STOP.",
        ]
        content = "BREAKROOM COFFEE COMPLAINTS LOG\nStarted by: someone who cares\nFormat: Name / Complaint\n\n"
        content += "\n".join(random.sample(complaints, random.randint(4, len(complaints))))
        content += f"\n\nNOTE FROM FACILITIES: We hear you. New coffee maker ordered. ETA {random.choice(['2 weeks','next fiscal quarter','unknown at this time'])}.\n"
        return content

    elif "printer" in fname_hint:
        events = [(rdate(2019,2026).strftime('%m/%d/%Y'), rname(), random.choice([
            "Paper jam, Tray 2. Cleared after 15 minutes.",
            "Out of toner. Replacement on order.",
            "Driver error on all Windows 11 machines. IT escalated.",
            "Printed 400 pages of a test page. Unknown origin.",
            "Offline for 3 hours, cause unknown, resolved spontaneously.",
            "Paper tray physically broken. Taped by unknown good samaritan.",
            "Network print queue stuck. Spooler restart required.",
            "Printed in mirror image. Cause: user error (flipped paper).",
            "Caught fire. Small fire. Under control. Facilities notified.",
        ])) for _ in range(random.randint(10,20))]
        content = "PRINTER INCIDENT LOG — Building A 2nd Floor\nMaintained by: whoever is most annoyed at the time\n\n"
        content += f"{'Date':<14}{'Reported By':<30}{'Incident'}\n" + "-"*80 + "\n"
        for dt, name, incident in events:
            content += f"{dt:<14}{name:<30}{incident}\n"
        return content

    return "Personal file.\n"


def gen_budget_csv():
    name = rname()
    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    yr = random.randint(2019, 2026)
    content = f"Personal Budget Tracker — {name} — {yr}\n"
    content += "Month,Income,Rent,Groceries,Utilities,Gas,Entertainment,Misc,Savings\n"
    income = random.randint(3200, 6800)
    for m in months:
        rent = random.randint(1100, 1900)
        groceries = random.randint(200, 450)
        utilities = random.randint(80, 220)
        gas = random.randint(60, 180)
        ent = random.randint(50, 300)
        misc = random.randint(30, 400)
        savings = income - rent - groceries - utilities - gas - ent - misc
        content += f"{m},{income},{rent},{groceries},{utilities},{gas},{ent},{misc},{max(0,savings)}\n"
    return content


def generate_personal_clutter():
    generated = 0

    # Journal entries scattered around
    for emp_name, dept, desc in JOURNAL_EMPLOYEES:
        num_entries = random.randint(4, 12)
        for i in range(num_entries):
            dt = rdate(2016, 2026)
            fname = f"journal_{emp_name.split()[0].lower()}_{dt.strftime('%Y%m%d')}.txt"
            subdir = random.choice(["Desktop","Downloads","Temp","Stuff","Random"])
            write_file(BASE / subdir / fname, gen_journal_entry(emp_name, dept, desc))
            tick("Clutter-Journal"); generated += 1

    # Humor files
    humor_files = {
        "office_chili_cookoff_rankings.csv": "chili",
        "fantasy_football_2022.csv": "fantasy_football",
        "who_keeps_stealing_my_yogurt.txt": "yogurt",
        "breakroom_coffee_complaints.txt": "coffee",
        "printer_incidents.csv": "printer",
    }
    for fname, hint in humor_files.items():
        subdir = random.choice(["Desktop","Shared/Old","Temp"])
        write_file(BASE / subdir / fname, gen_humor_file(hint))
        tick("Clutter-Humor"); generated += 1

    # FINAL naming chaos
    base_content = "Budget proposal for new MRI unit expansion — NorthStar Regional Health Network\n\nVersion tracking is hard. Please use the one that says FINAL at the end.\n\nActual content: see attached slides (not attached).\nActual budget: ask {}\n".format(random.choice(MANAGERS))
    for fname in ["FINAL.txt","FINAL_v2.txt","FINAL_v2_REAL.txt","FINAL_v2_REAL_FINAL.txt","FINAL_v2_REAL_FINAL_USE_THIS_ONE.txt"]:
        write_file(BASE / "Desktop" / fname, base_content + f"\nFile version identifier: {fname}\n")
        tick("Clutter-Final"); generated += 1

    # Budget CSVs
    for i in range(10):
        fname = f"personal_budget_{random.randint(2018,2025)}.csv"
        subdir = random.choice(["Downloads","Desktop","Stuff"])
        write_file(BASE / subdir / fname, gen_budget_csv())
        tick("Clutter-Budget"); generated += 1

    # Grocery lists
    for i in range(10):
        items = random.sample([
            "milk","eggs","bread","butter","chicken","ground beef","pasta","rice",
            "broccoli","spinach","yogurt","cheese","coffee","tea","juice","apples",
            "bananas","oranges","potatoes","onions","garlic","olive oil","canned beans",
            "cereal","paper towels","dish soap","shampoo","toothpaste","ibuprofen",
        ], random.randint(8, 18))
        content = f"Grocery List — {rdate(2018,2026).strftime('%m/%d/%Y')}\n\n"
        content += "\n".join(f"[ ] {item}" for item in items)
        fname = f"grocery_list_{random.randint(1,99)}.txt"
        write_file(BASE / random.choice(["Desktop","Downloads","Temp"]) / fname, content)
        tick("Clutter-Grocery"); generated += 1

    # Vacation planning
    for i in range(8):
        dest = random.choice(["Hawaii","Costa Rica","New Orleans","Sedona AZ","Pacific Coast Highway","Smoky Mountains","Scotland","Iceland"])
        dt = rdate(2019, 2026)
        content = f"""Vacation Planning — {dest}
Dates: {dt.strftime('%B')} {dt.year}

Flight Options:
  Option 1: {random.choice(['Southwest','Delta','United','American'])} — ${random.randint(180,650)} RT — {random.randint(0,2)} stops
  Option 2: {random.choice(['Southwest','Delta','United','Alaska'])} — ${random.randint(200,700)} RT — {random.randint(0,1)} stops

Hotel:
  {random.choice(['The Hilton Garden Inn','A nice Airbnb near downtown','Marriott Bonvoy property','Budget motel — might upgrade','Staying with family'])}
  Estimated cost: ${random.randint(90,350)}/night x {random.randint(3,10)} nights

Things to do:
  - {random.choice(['Tour the historic district','Hiking — research trails','Food tour','Museum visit','Beach time','National park entry'])}
  - {random.choice(['Rent a car or use Lyft','Local cooking class','Snorkeling excursion','Night market'])}
  - {random.choice(['Day trip to nearby town','Whale watching','Sunset dinner reservation','Farmers market'])}

Budget estimate: ${random.randint(1200,5500):,} total (not including souvenirs, obviously)

Need to submit PTO request by: {(dt - timedelta(days=random.randint(30,90))).strftime('%m/%d/%Y')}
"""
        fname = f"vacation_planning_{dest.replace(' ','_').lower()}_{dt.year}.txt"
        write_file(BASE / random.choice(["Desktop","Downloads","Stuff"]) / fname, content)
        tick("Clutter-Vacation"); generated += 1

    # Recipe files
    recipes = [
        ("slow_cooker_pot_roast", "3-4 lb chuck roast\n2 cups beef broth\n4 potatoes, quartered\n3 carrots, chunked\n1 packet onion soup mix\nCook on LOW 8 hours. Fall apart tender."),
        ("banana_bread", "3 ripe bananas\n1/3 cup melted butter\n3/4 cup sugar\n1 egg\n1 tsp vanilla\n1 1/2 cup flour\n1 tsp baking soda\nBake 350F 60 minutes."),
        ("chicken_tikka_masala", "2 lbs chicken, cubed\n1 can crushed tomato\n1 cup cream\n2 tsp garam masala\n1 tsp cumin\n1 tsp turmeric\nGarlic, ginger, butter. 30 mins."),
        ("guacamole", "3 ripe avocados\n1 lime, juiced\n1/2 onion, diced\n1 tomato, diced\nCilantro, salt, jalapeño optional.\nMash. Don't over mix."),
    ]
    for rname_slug, ingredients in recipes:
        fname = f"recipe_{rname_slug}.txt"
        content = f"Recipe: {rname_slug.replace('_',' ').title()}\n\nIngredients / Steps:\n{ingredients}\n\nFrom: {rname()}'s personal collection\n"
        write_file(BASE / random.choice(["Desktop","Stuff","Random"]) / fname, content)
        tick("Clutter-Recipe"); generated += 1

    return generated

print("Starting personal/clutter document generation...")
clutter_count = generate_personal_clutter()
print(f"Clutter documents done: {clutter_count}")

# ─── ARCHIVE / ABANDONED DOCUMENT GENERATORS ─────────────────────────────────

def gen_old_policy(title, old_org="Westfield General Hospital Network"):
    yr = random.randint(2016, 2018)
    suffix = random.choice(["_v1","_v2","_DRAFT","_OLD","_DO_NOT_USE","_LEGACY","_ARCHIVE_ONLY"])
    content = f"""{old_org}
POLICY DOCUMENT — ARCHIVED
{title}
Version: {suffix.strip('_')}
Original Issue Date: {rdate(yr, yr).strftime('%m/%d/%Y')}
Last Revised: {rdate(yr, yr+1).strftime('%m/%d/%Y')}
Status: SUPERSEDED — DO NOT USE FOR CURRENT OPERATIONS

NOTE: This policy has been superseded following the 2019 rebrand to NorthStar Regional Health Network.
Current policy available in the Policy & Procedure Management System.

---

POLICY STATEMENT
{random.choice([
    'All employees are required to complete annual compliance training using the MedTrack v1 LMS portal.',
    'Patient records must be maintained in the legacy WESTFIELD EMR system and archived per retention schedule.',
    'All vendor access must be approved by the IT Director using the paper-based request form (FORM-IT-07).',
    'Employee timesheets are to be submitted via the OldHR Portal no later than Sunday at midnight.',
    'HIPAA training must be completed within 30 days of hire using the CD-ROM based training module.',
    'All outbound faxes containing PHI must be logged in the paper PHI Fax Transmittal Log at each nursing station.',
])}

SCOPE
All employees of {old_org}, including medical staff, contractors, and volunteers.

PROCEDURE
[Content omitted — see current policy for updated procedure]

EFFECTIVE DATE: {rdate(yr, yr).strftime('%m/%d/%Y')}
REVIEW DATE: {rdate(yr+1, yr+2).strftime('%m/%d/%Y')}
APPROVED BY: {random.choice(MANAGERS)}

ARCHIVE NOTE: Retained for historical reference only. Not applicable to current operations.
"""
    return content, suffix


def generate_archive_documents():
    generated = 0

    old_policies = [
        "HIPAA Privacy Notice — Patient Rights",
        "Employee Code of Conduct",
        "Social Media Policy",
        "Workplace Violence Prevention Policy",
        "Remote Access and VPN Policy",
        "Mobile Device Management Policy",
        "PHI Fax and Email Transmission Policy",
        "Visitor Access Policy",
        "Vendor Management Policy",
        "Password and Account Security Policy",
        "Media Disposal and Sanitization Policy",
        "Incident Response Policy",
        "Backup and Recovery Policy",
        "Acceptable Use Policy — Electronic Systems",
        "Employee Handbook Section 4 — Attendance",
    ]

    for policy_title in old_policies:
        for _ in range(random.randint(2, 4)):
            content, suffix = gen_old_policy(policy_title)
            safe_title = policy_title.replace(' ','_').replace('—','').replace('/','_')[:40]
            fname = f"{safe_title}{suffix}.txt"
            subdir = random.choice(["Archive/Old_HR","Shared/Old","DoNotDelete"])
            write_file(BASE / subdir / fname, content)
            tick("Archive-Policy"); generated += 1

    # Old payroll archives
    for yr in range(2016, 2018):
        for i in range(random.randint(5,10)):
            dt = rdate(yr, yr)
            fname = f"payroll_archive_{yr}_{dt.strftime('%m')}_OLD.txt"
            org = "Westfield General Hospital Network"
            content = f"""{org}
ARCHIVED PAYROLL RECORD
Period: {dt.strftime('%B %Y')}
System: OldHR Portal v2.1
Export Date: {dt.strftime('%m/%d/%Y')}

[LEGACY FORMAT — Migrated from OldHR to MedTrack Payroll in 2019]
[Do not modify — retained per 7-year document retention policy]

Department: {random.choice(DEPARTMENTS)}
Total Employees: {random.randint(10,40)}
Gross Payroll: ${random.randint(80000,400000):,}
"""
            write_file(BASE / "Archive/Payroll2017" / fname, content)
            tick("Archive-Payroll"); generated += 1

    # Duplicate records (simulated)
    for i in range(30):
        dt = rdate(2017, 2021)
        name = rname()
        mrn = rmrn()
        content = f"""[DUPLICATE RECORD — DO NOT USE]
This record was created during system migration from MedTrack v1 to MedTrack v2.
Original MRN: {mrn}
Patient Name: {name}
Duplicate flagged by: {rname()}, Data Integrity Team
Date Flagged: {dt.strftime('%m/%d/%Y')}
Resolution: Merged into primary record. This copy retained for audit trail.
"""
        fname = f"DUPLICATE_{mrn}_{name.replace(' ','_')}.txt"
        write_file(BASE / "Patients/Archived" / fname, content)
        tick("Archive-Dup"); generated += 1

    # COVID-era policy documents
    covid_docs = [
        ("visitor_restriction_policy_COVID19.txt", "VISITOR RESTRICTION POLICY — COVID-19\nEffective: March 15, 2020\n\nDue to the ongoing COVID-19 public health emergency, NorthStar Regional Health Network is implementing the following visitor restrictions effective immediately:\n\n1. No visitors permitted except for:\n   - Labor and delivery patients (1 support person)\n   - Pediatric patients (1 parent/guardian)\n   - End of life situations (2 visitors, screened)\n   - Surgical patients (1 escort, waiting area only)\n\n2. All visitors must:\n   - Complete COVID-19 screening at all entrances\n   - Wear a surgical mask at all times\n   - Maintain 6-foot distancing\n\n3. This policy will be reviewed every 2 weeks.\n\nApproved by: Chief Medical Officer\nDate: March 14, 2020\n"),
        ("telehealth_expansion_2020.txt", "TELEHEALTH PROGRAM EXPANSION — EMERGENCY AUTHORIZATION\nDate: April 2, 2020\n\nIn response to COVID-19, NorthStar Regional Health Network is expanding telehealth services to maintain continuity of care.\n\nPlatform: Doxy.me (HIPAA-compliant)\nService Lines: Primary Care, Behavioral Health, Chronic Disease Management, Medication Management\nReimbursement: CMS telehealth flexibilities under PHE now active\nDocumentation: Standard visit note with GT modifier for billing\n\nAll providers must complete 1-hour telehealth orientation before seeing patients virtually.\n\nQuestions: telehealth-support@northstar-health.internal\n"),
        ("ppe_conservation_memo_2020.txt", "MEMORANDUM\nTO: All Clinical Staff\nFROM: Chief Nursing Officer\nDATE: March 25, 2020\nRE: PPE Conservation Guidelines During COVID-19 Shortage\n\nDue to national supply chain disruptions, we are implementing the following PPE conservation guidelines:\n\n1. N95 respirators — extended use up to 8 hours unless visibly soiled or wet\n2. Surgical masks — single patient room use, extended up to 4 hours in non-COVID areas\n3. Isolation gowns — reserved for confirmed/suspected COVID patients\n4. Face shields — shared with disinfection between uses (approved protocol attached)\n\nThis is a temporary measure. We are actively working with suppliers to restore normal inventory.\n\nThank you for your resilience and dedication.\n"),
        ("return_to_work_guidance_2021.txt", "RETURN TO NORMAL OPERATIONS — PHASED APPROACH\nDate: June 1, 2021\n\nAs COVID-19 vaccination rates improve and case counts decline, NorthStar Regional Health Network will begin phased return to normal operations:\n\nPhase 1 (June 2021): Resume elective procedures up to 75% capacity\nPhase 2 (August 2021): Relax visitor restrictions to 1 visitor per patient\nPhase 3 (Q4 2021): Full operational restoration pending public health guidance\n\nAll staff who are unvaccinated must continue to wear an N95 or equivalent in all patient areas.\n\nMask policy updates will be communicated by department.\n"),
    ]
    for fname, content in covid_docs:
        subdir = random.choice(["Compliance/HIPAA","Shared/Old","Archive/Old_HR"])
        write_file(BASE / subdir / fname, content)
        tick("Archive-Covid"); generated += 1

    # Random DoNotDelete files
    for i in range(20):
        dt = rdate(2016, 2021)
        fname = f"important_do_not_delete_{random.randint(1,999)}.txt"
        content = f"""THIS FILE IS IMPORTANT — DO NOT DELETE
Created: {dt.strftime('%m/%d/%Y')}
Created by: {rname()}

{random.choice([
    'Contains configuration backup for old MedTrack v1 system. Required for audit purposes.',
    'Archive of 2017 year-end payroll reconciliation. Finance has a copy.',
    'Old template used for patient intake forms before the EHR migration. Keep for reference.',
    'Spreadsheet of vendor contacts from 2018. Some may still be valid.',
    'Notes from the 2016 HIPAA audit. Recommendations were implemented per compliance plan.',
    'Legacy report format required by old insurance company. They no longer contract with us but who knows.',
])}

If you have questions contact: {remail(rname())}
"""
        write_file(BASE / "DoNotDelete" / fname, content)
        tick("Archive-DNDelete"); generated += 1

    return generated

print("Starting archive document generation...")
archive_count = generate_archive_documents()
print(f"Archive documents done: {archive_count}")

# ─── FILLER DOCUMENTS TO REACH 3000+ ─────────────────────────────────────────

def gen_filler_documents():
    generated = 0
    current_count = counter[0]
    needed = max(0, 3000 - current_count)

    filler_types = [
        lambda: (f"HR/Personnel/Active/policy_ack_{rname().replace(' ','_')}_{rdate(2016,2026).strftime('%Y%m%d')}.txt",
            f"NorthStar Regional Health Network\nPOLICY ACKNOWLEDGMENT FORM\n\nI, {rname()}, acknowledge receipt and understanding of the following policies:\n- HIPAA Privacy Policy\n- Social Media Policy\n- Workplace Violence Prevention Policy\n- Code of Conduct\n- Acceptable Use Policy\n\nEmployee ID: {rempid()}\nDate: {rdate(2016,2026).strftime('%m/%d/%Y')}\nDepartment: {random.choice(DEPARTMENTS)}\nSignature: ___________________________\n"),
        lambda: (f"Patients/{random.randint(2016,2026)}/progress_note_{rmrn()}_{rdate(2016,2026).strftime('%Y%m%d')}.txt",
            f"NorthStar Regional Health Network — PROGRESS NOTE\nDate: {rdate(2016,2026).strftime('%m/%d/%Y')}\nMRN: {rmrn()}\nPatient: {rname()}\nProvider: {random.choice(PHYSICIANS)}\n\nPatient seen today for follow-up. {random.choice(['Clinically stable. No new complaints.','Symptom improvement noted since last visit.','Patient reports continued improvement with current regimen.','New medication tolerating well. Follow up in 4 weeks.','Referred to specialist — see order.','Lab results reviewed with patient.'])}\n\nVitals: BP {random.randint(110,155)}/{random.randint(65,95)} | HR {random.randint(60,100)} | Temp {round(random.uniform(97.5,99.5),1)}F\n\nPlan: Continue current management. RTC as scheduled.\nSigned: {random.choice(PHYSICIANS)}\n"),
        lambda: (f"HR/Training/training_cert_{rname().replace(' ','_')}_{rdate(2018,2026).strftime('%Y%m%d')}.txt",
            f"NorthStar Regional Health Network\nTRAINING CERTIFICATE\n\nThis certifies that {rname()} has successfully completed:\n{random.choice(['HIPAA Privacy & Security Annual Training','BLS Recertification','Fire Safety Training','Workplace Violence Prevention','EHR Advanced User Training','Fall Prevention Competency'])}\n\nDate Completed: {rdate(2018,2026).strftime('%m/%d/%Y')}\nScore: {random.randint(80,100)}%\nCEUs Awarded: {random.choice(['0.5','1.0','1.5','0'])}\nExpires: {rdate(2024,2027).strftime('%m/%d/%Y')}\nIssued by: NorthStar Learning Management System\n"),
        lambda: (f"Billing/{random.randint(2016,2026)}/claim_{rmrn()}_{rdate(2016,2026).strftime('%Y%m%d')}.txt",
            f"NorthStar Regional Health Network\nINSURANCE CLAIM RECORD\nClaim #: CLM-{random.randint(1000000,9999999)}\nDate Submitted: {rdate(2016,2026).strftime('%m/%d/%Y')}\nMRN: {rmrn()}\nPatient: {rname()}\nInsurance: {random.choice(INSURANCE_COMPANIES)}\nDOS: {rdate(2016,2026).strftime('%m/%d/%Y')}\nProvider: {random.choice(PHYSICIANS)}\nCPT: {random.choice(CPT_CODES)[0]}\nICD-10: {random.choice(DIAGNOSES)[0]}\nBilled Amount: ${random.randint(150,2500):,}\nStatus: {random.choice(['Paid','Denied — Appeal Filed','Pending','Partially Paid','Void and Resubmit'])}\n"),
        lambda: (f"IT/Tickets/Closed/vpn_request_{rempid()}_{rdate(2017,2026).strftime('%Y%m%d')}.txt",
            f"NorthStar Regional Health Network — IT\nVPN ACCESS REQUEST\nDate: {rdate(2017,2026).strftime('%m/%d/%Y')}\nRequestor: {rname()}\nEmployee ID: {rempid()}\nDepartment: {random.choice(DEPARTMENTS)}\nBusiness Justification: {random.choice(['Remote work arrangement approved by manager','On-call coverage requiring after-hours system access','Telecommute arrangement — 2 days/week','Travel to satellite clinic — need remote EHR access'])}\nManager Approval: {random.choice(MANAGERS)}\nIT Approval: {rname()}\nAccess Level: {random.choice(['Standard Employee VPN','Clinical VPN — EHR Access','Administrative VPN Only','Full Access — Approved by CISO'])}\nStatus: {random.choice(['Approved','Approved','Approved','Denied — See Comments'])}\n"),
        lambda: (f"Compliance/Audits/audit_finding_{rdate(2017,2026).strftime('%Y%m%d')}_{random.randint(100,999)}.txt",
            f"NorthStar Regional Health Network\nAUDIT FINDING\nAudit Date: {rdate(2017,2026).strftime('%m/%d/%Y')}\nAudit Type: {random.choice(['Internal Compliance Audit','External HIPAA Review','CMS Conditions of Participation','Joint Commission Survey Finding','OIG Work Plan Audit'])}\nFinding: {random.choice(['Training completion rates below 90% threshold in two departments.','Incomplete documentation in 3 of 25 sampled charts.','Business Associate Agreement missing for one vendor.','PHI in unencrypted email — isolated incident.','Access controls not reviewed within required annual timeframe.'])}\nSeverity: {random.choice(['Minor','Moderate','Significant'])}\nCAP Assigned To: {random.choice(MANAGERS)}\nCAP Due Date: {rdate(2024,2027).strftime('%m/%d/%Y')}\nStatus: {random.choice(['Open','Closed — Remediated','In Progress'])}\n"),
    ]

    for i in range(needed + 200):  # generate a buffer
        fn_maker = random.choice(filler_types)
        fpath_str, content = fn_maker()
        fpath = BASE / fpath_str
        write_file(fpath, content)
        tick("Filler"); generated += 1

    return generated

print("Generating filler documents to reach 3000+ target...")
filler_count = gen_filler_documents()
print(f"Filler documents done: {filler_count}")

# ─── FINAL SUMMARY ───────────────────────────────────────────────────────────

print("\n" + "="*60)
print("NORTHSTAR DOCUMENT ECOSYSTEM — GENERATION COMPLETE")
print("="*60)

total = counter[0]
print(f"Total documents generated: {total}")
print(f"Target was: {total_target}")
print(f"Status: {'PASS' if total >= total_target else 'UNDER TARGET'}")

# Count by directory
import subprocess
result = {}
for folder in ["HR","Patients","Billing","Insurance","IT","Executive","Compliance","Legal","Archive","Desktop","Downloads","Temp","Stuff","Random","DoNotDelete","Shared"]:
    p = BASE / folder
    if p.exists():
        count = sum(1 for _ in p.rglob("*.txt")) + sum(1 for _ in p.rglob("*.csv"))
        result[folder] = count

print("\nFILE COUNTS BY CATEGORY:")
for folder, count in sorted(result.items(), key=lambda x: -x[1]):
    print(f"  {folder:<20} {count:>5} files")

print(f"\nAll files written to: {BASE}")
print("Generation complete.")
