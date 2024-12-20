from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Any, Optional, Dict
from fastapi.middleware.cors import CORSMiddleware
import json

import requests

import utilizes as utz
from models import *
# from sheets import *
import sheets as sht

origins = [
    "https://linkedin-scraping-frontend.onrender.com/",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/employees")
async def get_employeeInfo(data: FormData):
    mail = data.email
    subject = data.subject
    countryList = [countryCode.lower() for countryCode in data.selectedCountries]
    companyList = data.companyPairs

    employeeInfoList = await utz.fetch_employeeInfo(companyList=companyList, countryList=countryList, keyword=subject)

    spreadsheet = sht.auth_sheet()
    sheet = sht.init_sheet(spreadsheet)
    

    contactInfoList = utz.fetch_contactInfo(EmployeeProfileList=employeeInfoList)

    sht.write_sheet(sheet, employeeInfoList, contactInfoList)

@app.post("/contactInfo")
def get_contactInfo(employeeInfoList: List[EmloyeeProfile]):
    print(utz.fetch_contactInfo(EmployeeProfileList=employeeInfoList))


