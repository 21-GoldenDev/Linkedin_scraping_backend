from pydantic import BaseModel
from typing import List, Any, Optional, Dict

class CompanyPair(BaseModel):
    companyURL: str
    companyType: str

class FormData(BaseModel):
    email: str
    subject: str
    selectedCountries: List[str]
    companyPairs: List[CompanyPair]

class EmloyeeProfile(BaseModel):
    profile_url: str
    first_name: str
    last_name: str
    full_name: str
    headline: str
    country: str
    company_url: str
    company_name: str
    type: str