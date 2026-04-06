
from pydantic import BaseModel, Field
from enum import Enum


class AadharRequest(BaseModel):
    aadhar_number: str = Field(..., pattern=r'^\d{12}$', min_length=12, max_length=12, example="123456789012")

class VoterRequest(BaseModel):
    epic_number: str = Field(..., pattern=r'^[A-Z]{3}[0-9]{7}$', min_length=10, max_length=10, example="XXX0000000")
    # States - set True for the state you want to search
    Andaman_Nicobar_Islands: bool = False
    Andhra_Pradesh: bool = False
    Arunachal_Pradesh: bool = False
    Assam: bool = False
    Bihar: bool = False
    Chandigarh: bool = False
    Chhattisgarh: bool = False
    Dadra_Nagar_Haveli_Daman_Diu: bool = False
    Goa: bool = False
    Gujarat: bool = False
    Haryana: bool = False
    Himachal_Pradesh: bool = False
    Jammu_and_Kashmir: bool = False
    Jharkhand: bool = False
    Karnataka: bool = False
    Kerala: bool = False
    Ladakh: bool = False
    Lakshadweep: bool = False
    Madhya_Pradesh: bool = False
    Maharashtra: bool = False
    Manipur: bool = False
    Meghalaya: bool = False
    Mizoram: bool = False
    Nagaland: bool = False
    NCT_OF_Delhi: bool = False
    Odisha: bool = False
    Puducherry: bool = False
    Punjab: bool = False
    Rajasthan: bool = False
    Sikkim: bool = False
    Tamil_Nadu: bool = False
    Telangana: bool = False
    Tripura: bool = False
    Uttar_Pradesh: bool = False
    Uttarakhand: bool = False
    West_Bengal: bool = False

class PanRequest(BaseModel):
    pan_number: str = Field(..., pattern=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', example="XXXXX1234X")
    aadhar_number: str = Field(..., pattern=r'^\d{12}$', min_length=12, max_length=12, example="123456789012")

class AdaniRequest(BaseModel):
    ca_number: str = Field(..., pattern=r'^\d{9}$', example="123456789")
   
class APEPDCLRequest(BaseModel):
    scno: str = Field(..., pattern=r'^\d{16}$', example="0000000000000000")


class DVVNLRequest(BaseModel):
    account_number: str = Field(..., pattern=r'^\d{10}$', example="1234567890")
    district: str = Field(..., pattern=r'^[A-Z][a-z]+(?:\s[A-Z][a-z]+)*$', example="Msssaxxxx")

class MaharashtraElectricityRequest(BaseModel):
    consumer_number: str = Field(..., pattern=r'^\d{12}$', min_length=12, max_length=12, example="123456789012")

class PUVNLRequest(BaseModel):
    account_number: str = Field(..., pattern=r'^\d{10}$', example="1234567890")
    district: str = Field(..., pattern=r'^[A-Z][a-z]+(?:\s[A-Z][a-z]+)*$', example="Msssaxxxx")


class TGSPDCLRequest(BaseModel):
    service_number: str = Field(..., pattern=r'^\d{9}$', example="123456789")

class TorrentPowerRequest(BaseModel):
    service_number: str = Field(..., pattern=r'^\d{9}$', example="123456789")
    # Cities - set True for the city you want to search
    Agra: bool = False
    Ahmedabad: bool = False
    Bhiwandi: bool = False
    Dahej: bool = False
    Dadra_Nagar_Haveli: bool = False
    Dholera: bool = False
    Diu_Daman: bool = False
    Shil_Mumbra_Kalwa: bool = False
    Surat: bool = False

class BESCOMRequest(BaseModel):
    account_id: str = Field(..., pattern=r'^\d{10}$', example="1234567890")

class UPCLRequest(BaseModel):
    account_number: str = Field(..., pattern=r'^\d{11}$', example="12345678900")  

class GVCLCompanyCode(str, Enum):
    MGVCL = "MGVCL"
    DGVCL = "DGVCL"
    PGVCL = "PGVCL"
    UGVCL = "UGVCL"

class ALL_GVCLRequest(BaseModel):
    consumer_number: str = Field(..., pattern=r'^\d{11}$', example="12345678900")
    DGVCL: bool = False
    MGVCL: bool = False
    PGVCL: bool = False
    UGVCL: bool = False

class TnpdclRequest(BaseModel):
    consumer_number: str = Field(..., pattern=r'^\d{11}$', example="12345678900")

class TpddlRequest(BaseModel):
    ca_number: str = Field(..., pattern=r'^\d{11}$', example="12345678900")


class TPLRequest(BaseModel):
    part1: str = Field(..., pattern=r'^\d{4}$', example="1234")
    part2: str = Field(..., pattern=r'^\d{4}$', example="1234")
    part3: str = Field(..., pattern=r'^\d{4}$', example="1234")

class Mescom_rRequest(BaseModel):
    consumer_no: str = Field(..., pattern=r'^\d{7}$', example="1234567")

class UHBVNRequest(BaseModel):
    account_number: str = Field(..., pattern=r'^\d{10}$', example="1234567890")

class DHBVNRequest(BaseModel):
    account_number: str = Field(..., pattern=r'^\d{10}$', example="1234567890")

class DelhiStampDutyRequest(BaseModel):
    certificate_no: str
    state: str = "IN_DL"
    stamp: str
    certificate_issued_date: str

class GujratStampDutyRequest(BaseModel):
    certificate_no: str
    state: str = "IN_GJ"
    stamp: str
    certificate_issued_date: str

class KarnatkaStampDutyRequest(BaseModel):
    certificate_no: str
    state: str = "IN_KA"
    stamp: str
    certificate_issued_date: str    
    

class RajasthanStampDutyRequest(BaseModel):
    certificate_no: str
    state: str = "IN_RJ"
    stamp: str
    certificate_issued_date: str      

class PunjabStampDutyRequest(BaseModel):
    certificate_no: str
    state: str = "IN_PB"
    stamp: str
    certificate_issued_date: str     

class UttarPradeshStampDutyRequest(BaseModel):
    certificate_no: str
    state: str = "IN_UP"
    stamp: str
    certificate_issued_date: str     