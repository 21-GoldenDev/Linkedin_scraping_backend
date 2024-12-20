import requests, time
from proxycurl.asyncio import Proxycurl, do_bulk
from typing import List
import csv, json

from models import *

proxycurl = Proxycurl()

async def fetch_employeeInfo(companyList: List[CompanyPair], countryList: List[str], keyword: str):

    employeeList = await asyncio.gather(
        *(proxycurl.linkedin.company.employee_search(
            keyword_regex = keyword,
            linkedin_company_profile_url = company.companyURL 
        ) for company in companyList)
    )

    for i, company in enumerate(companyList):
        employeeList[i]["type"] = company.companyType
        employeeList[i]["company_url"] = company.companyURL
    
    # print(employeeList)

    output_file = "employee_data0.json"

    # Write the result to the JSON file
    with open(output_file, "w") as f:
        json.dump(employeeList, f, indent=4)

    print(f"Employee data written to {output_file}")

    concurrent_process = [
        employee_filter(data, employee, countryList)
        for employee in employeeList for data in employee.get('employees', [])
    ]

    employeeProfileGather = await asyncio.gather(*concurrent_process)
    employeeProfileList = [profile for profile in employeeProfileGather if profile is not None]

    # print(employeeProfileList)
    
    output_file = "employee_data1.json"

    # Write the result to the JSON file
    with open(output_file, "w") as f:
        json.dump(employeeProfileList, f, indent=4)

    print(f"Employee data written to {output_file}")



    return employeeProfileList

async def employee_filter(data, employee, countryList):
    
    url = data.get('profile_url', {})
    try:
        profile = await asyncio.run(proxycurl.linkedin.person.get(
            linkedin_profile_url=url
        ))
        if profile.get('country').lower() in countryList:
            company_profile = await asyncio.run(proxycurl.linkedin.company.get(
                url = employee.get('company_url')
            ))
            return {
                "profile_url": url,
                "first_name": profile.get('first_name'),
                "last_name": profile.get('last_name'),
                "full_name": profile.get('full_name'),
                "headline": profile.get('headline'),
                "country": profile.get('country'),
                "company_url": employee.get('company_url'),
                "company_name": company_profile.get('name'),
                "type": employee.get('type'),
            }
    except:
        print("Error")
    return None

def fetch_contactInfo(EmployeeProfileList):

    print(EmployeeProfileList)

    url = "https://app.fullenrich.com/api/v1/contact/enrich/bulk"

    datas = []

    for employee in EmployeeProfileList:
        data_entry = {
            "firstname": employee.first_name,
            "lastname": employee.last_name,
            "company_name": employee.company_name,
            "linkedin_url": employee.profile_url,
            "enrich_fields": ["contact.emails", "contact.phones"]
        }
        datas.append(data_entry)

    payload = {
        "name": "EmployeeContactInfo",
        "datas": datas
    }
    headers = {
        "Authorization": "Bearer 01ae77fa-f631-4ec5-9587-668422b39ec6",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    contactInfoList = []
    try:
        enrichment_id = response.json().get("enrichment_id")
        if enrichment_id is None:
            raise ValueError("Enrichment ID not found in the response")
        
        url = f"https://app.fullenrich.com/api/v1/contact/enrich/bulk/{enrichment_id}"        
        print(f"URL: {url}")

        try:
            response = wait_for_finished_status(url, headers)
            print("Final response:", response)
        except Exception as e:
            print("Error:", e)

        contactDataList = response.get("datas", [])

        for contactData in contactDataList:
            contact_info = contactData.get("contact", {})

            # Extract phone number
            phone = None
            phones = contact_info.get("phones", [])
            if phones:
                phone = phones[0].get("number")  # Get the first phone number

            # Extract email
            email = None
            emails = contact_info.get("emails", [])
            if emails:
                email = emails[0].get("email")
            
            print({"phone": phone, "email": email})

            contactInfoList.append({"phone": phone, "email": email})
        return contactInfoList

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def wait_for_finished_status(url, headers, check_interval=5, timeout=600):
    start_time = time.time()

    while time.time() - start_time < timeout:
        response = requests.request("GET", url, headers=headers)
        
        # Raise an exception if the request fails
        response.raise_for_status()

        # Parse the JSON response
        response_data = response.json()
        status = response_data.get("status")

        # Check if the status is 'FINISHED'
        if status == "FINISHED":
            return response_data

        # Print current status for debugging purposes
        print(f"Current status: {status}. Waiting...")

        # Wait before the next check
        time.sleep(check_interval)

    # If the loop completes, raise a timeout exception
    raise TimeoutError("Timeout: Status did not become 'FINISHED' within the given timeout.")


