import gspread
from oauth2client.service_account import ServiceAccountCredentials

def auth_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name('./storied-program-444012-t5-e2f612fe318a.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Linkedin Employee")
    return spreadsheet

def init_sheet(spreadsheet):
    try:
        sheet = spreadsheet.worksheet("Employee Results")
    except:
        sheet = spreadsheet.add_worksheet(title="Employee Results", rows="9999", cols="26")

    headers = [["Company Url", "Employee Profile", "Employee Headline", "Country",  "First Name", "Last Name", "Full Name", "Type", "Email", "Phone Number"]]
    sheet.update(values=headers, range_name='A1:J1')
    return sheet

def write_sheet(sheet, employeeInfoList, contactInfoList):
    for employee, contactInfo in zip(employeeInfoList, contactInfoList):
        company_url = employee.get('company_url')
        profile_url = employee.get('profile_url')
        headline = employee.get('headline')
        country = employee.get('country')
        first_name = employee.get('first_name')
        last_name = employee.get('last_name')
        full_name = employee.get('full_name')
        employee_type = employee.get('type')
        personal_email = contactInfo.get('email')
        personal_numbers = contactInfo.get('phone')


        try:
            data = [
                [company_url, profile_url, headline, country, first_name, last_name, full_name, employee_type, personal_email, personal_numbers]
            ]

            next_row = get_next_available_row(sheet)
            range_name = f'A{next_row}:J{next_row}'

            sheet.update(values=data, range_name=range_name)

            print("Employee datas written successfully!")
        except Exception as e:
            print(f"An error occurred: {e}")

def get_next_available_row(sheet):
    """
    Finds the first empty row in the Google Sheet.
    Assumes the sheet has data in the first column.
    """
    values = sheet.col_values(1)  # Get all values in column A (index 1)
    return len(values) + 1 