from fastapi import Request  
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field, constr
from typing import Optional
from dotenv import load_dotenv
import os
import sys
from contextlib import contextmanager
from tenacity import retry, stop_after_attempt, wait_exponential
import logging
from verified import verify_apepdcl
from verified.dvvnl import verify_dvvnl
from selenium import webdriver
from verified.maharashtra_electricity import verify_maharashtra
from utils import *
from verified import verify_aadhar, verify_voter_id, verify_pan, verify_adani
from verified.bescom import verify_bescom
from verified import *
from verified import verify_all_gvcl
from verified.tpddl import verify_tpddl
from verified.mescom_r import verify_mescom_r
from schema import *
from verified.stamp_delhi import verify_stamp_delhi
from verified.stamp_gujrat import verify_stamp_gujrat
from verified.stamp_rajasthan import verify_stamp_rajasthan


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captcha", ".env")
load_dotenv(env_path)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY is not set in the .env file")

app = FastAPI()

@contextmanager
def managed_driver():
    driver = setup_driver()
    try:
        yield driver
    finally:
        try:
            driver.quit()
        except Exception as e:
            logger.error(f"Error quitting driver: {e}")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def verify_with_retry(driver, verification_function, *args, **kwargs):
    return verification_function(driver, *args, **kwargs)

# ---------------------------------------------------------------
# ---------------------------------------------------------------

@app.post("/verify/aadhaar")
def verify_aadhaar_endpoint(data: AadharRequest):
    with managed_driver() as driver:
        try:
            result = verify_with_retry(driver, verify_aadhar, data.aadhar_number, OPENAI_API_KEY)
            return result
        except Exception as e:
            logger.error(f"Aadhaar verification failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Aadhaar verification failed: {str(e)}")
        
# ---------------------------------------------------------------

@app.post("/verify/voter")
def verify_voter_endpoint(data: VoterRequest):
    # Build state flags dict
    state_flags = {
        "Andaman_Nicobar_Islands": data.Andaman_Nicobar_Islands,
        "Andhra_Pradesh": data.Andhra_Pradesh,
        "Arunachal_Pradesh": data.Arunachal_Pradesh,
        "Assam": data.Assam,
        "Bihar": data.Bihar,
        "Chandigarh": data.Chandigarh,
        "Chhattisgarh": data.Chhattisgarh,
        "Dadra_Nagar_Haveli_Daman_Diu": data.Dadra_Nagar_Haveli_Daman_Diu,
        "Goa": data.Goa,
        "Gujarat": data.Gujarat,
        "Haryana": data.Haryana,
        "Himachal_Pradesh": data.Himachal_Pradesh,
        "Jammu_and_Kashmir": data.Jammu_and_Kashmir,
        "Jharkhand": data.Jharkhand,
        "Karnataka": data.Karnataka,
        "Kerala": data.Kerala,
        "Ladakh": data.Ladakh,
        "Lakshadweep": data.Lakshadweep,
        "Madhya_Pradesh": data.Madhya_Pradesh,
        "Maharashtra": data.Maharashtra,
        "Manipur": data.Manipur,
        "Meghalaya": data.Meghalaya,
        "Mizoram": data.Mizoram,
        "Nagaland": data.Nagaland,
        "NCT_OF_Delhi": data.NCT_OF_Delhi,
        "Odisha": data.Odisha,
        "Puducherry": data.Puducherry,
        "Punjab": data.Punjab,
        "Rajasthan": data.Rajasthan,
        "Sikkim": data.Sikkim,
        "Tamil_Nadu": data.Tamil_Nadu,
        "Telangana": data.Telangana,
        "Tripura": data.Tripura,
        "Uttar_Pradesh": data.Uttar_Pradesh,
        "Uttarakhand": data.Uttarakhand,
        "West_Bengal": data.West_Bengal
    }
    with managed_driver() as driver:
        try:
            result = verify_voter_id(driver, data.epic_number, state_flags, OPENAI_API_KEY)
            return result
        except Exception as e:
            logger.error(f"Voter ID verification failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Voter ID verification failed: {str(e)}")

# ---------------------------------------------------------------

@app.post("/verify/pan")
def verify_pan_endpoint(data: PanRequest):
    with managed_driver() as driver:
        try:
            result = verify_with_retry(driver, verify_pan, data.pan_number, data.aadhar_number)
            return result
        except Exception as e:
            logger.error(f"PAN verification failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"PAN verification failed: {str(e)}")
        
# ---------------------------------------------------------------

@app.post("/verify/adani")
def verify_adani_endpoint(data: AdaniRequest):
    with managed_driver() as driver:
        try:
            result = verify_with_retry(driver, verify_adani, data.ca_number)
            return result
        except Exception as e:
            logger.error(f"Adani verification failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Adani verification failed: {str(e)}")

# ---------------------------------------------------------------

@app.post("/verify/apepdcl")
def verify_apepdcl_endpoint(data: APEPDCLRequest):
    with managed_driver() as driver:
        try:
            result = verify_with_retry(driver, verify_apepdcl, data.scno, OPENAI_API_KEY)
            return result
        except Exception as e:
            logger.error(f"APEPDCL verification failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"APEPDCL verification failed: {str(e)}")
        
# ---------------------------------------------------------------

@app.post("/verify/dvvnl")
def verify_dvvnl_endpoint(data: DVVNLRequest):
    with managed_driver() as driver:
        try:
            result = verify_with_retry(driver, verify_dvvnl, data.account_number, data.district, OPENAI_API_KEY)
            return result
        except Exception as e:
            logger.error(f"DVVNL verification failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"DVVNL verification failed: {str(e)}")
        
# ---------------------------------------------------------------

@app.post("/verify/maharashtra-electricity")
def verify_maharashtra_endpoint(data: MaharashtraElectricityRequest):
    with managed_driver() as driver:
        try:
            result = verify_with_retry(driver, verify_maharashtra, data.consumer_number, OPENAI_API_KEY)
            return result
        except Exception as e:
            logger.error(f"Maharashtra Electricity verification failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Maharashtra Electricity verification failed: {str(e)}")

# ---------------------------------------------------------------

@app.post("/verify/puvnl")
def puvnl_verification(data: PUVNLRequest):
    driver = setup_driver()
    try:
        result = verify_puvnl(driver, data.account_number, data.district, OPENAI_API_KEY)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PUVNL verification failed: {str(e)}")
   
# ---------------------------------------------------------------

@app.post("/verify/tgspdcl")
def tgspdcl_verification(data: TGSPDCLRequest):
    driver = setup_driver()
    try:
        result = verify_tgspdcl(driver, data.service_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TGSPDCL verification failed: {str(e)}")
    finally:
        driver.quit()   

# ---------------------------------------------------------------

@app.post("/verify/torrent-power")
def torrent_power_verification(data: TorrentPowerRequest):
    # Build city flags dict
    city_flags = {
        "Agra": data.Agra,
        "Ahmedabad": data.Ahmedabad,
        "Bhiwandi": data.Bhiwandi,
        "Dahej": data.Dahej,
        "Dadra Nagar Haveli": data.Dadra_Nagar_Haveli,
        "Dholera": data.Dholera,
        "Diu - Daman": data.Diu_Daman,
        "Shil, Mumbra & Kalwa": data.Shil_Mumbra_Kalwa,
        "Surat": data.Surat
    }
    driver = setup_driver()
    try:
        result = verify_torrent_power(driver, data.service_number, city_flags)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Torrent Power verification failed: {str(e)}")
    finally:
        driver.quit()        

# ---------------------------------------------------------------

@app.post("/verify/bescom")
def bescom_verification(data: BESCOMRequest):
    driver = setup_driver()
    try:
        result = verify_bescom(driver, data.account_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BESCOM verification failed: {str(e)}")
    finally:
        driver.quit()

# ---------------------------------------------------------------

@app.post("/verify/upcl")
def upcl_verification(data: UPCLRequest):
    driver = setup_driver()
    try:
        result = verify_upcl(driver, data.account_number, OPENAI_API_KEY)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"UPCL verification failed: {str(e)}")
    finally:
        driver.quit()


# ---------------------------------------------------------------

@app.post("/verify/all_gvcl")
def all_gvcl_verification(data: ALL_GVCLRequest):
    # Build list of companies marked as True
    company_flags = {
        "DGVCL": data.DGVCL,
        "MGVCL": data.MGVCL,
        "PGVCL": data.PGVCL,
        "UGVCL": data.UGVCL
    }
    driver = setup_driver()
    try:
        result = verify_all_gvcl(driver, data.consumer_number, company_flags, OPENAI_API_KEY)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"All GVCL verification failed: {str(e)}")
    finally:
        driver.quit()

# ---------------------------------------------------------------

@app.post("/verify/tnpdcl")
def verify_tnpdcl_endpoint(data: TnpdclRequest):
    with managed_driver() as driver:
        try:
            result = verify_tnpdcl(driver, data.consumer_number, OPENAI_API_KEY)
            return result
        except Exception as e:
            logger.error(f"TNPCL verification failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"TNPCL verification failed: {str(e)}")     

# ---------------------------------------------------------------

@app.post("/verify/tpddll")
def verify_tpddl_endpoint(data: TpddlRequest):
    with managed_driver() as driver:
        try:
            result = verify_tpddl(driver, data.ca_number, OPENAI_API_KEY)
            return result
        except Exception as e:
            logger.error(f"TNPCL verification failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"TNPCL verification failed: {str(e)}")

# ---------------------------------------------------------------

@app.post("/verify/tpp")
def verify_tpl_api(request: TPLRequest):
    with managed_driver() as driver:
        try:
            result = verify_tpp(driver, request.part1, request.part2, request.part3)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
# ---------------------------------------------------------------

@app.post("/verify/mescom_r")
def verify_mescom_r_api(request: Mescom_rRequest):
    with managed_driver() as driver:
        try:
            result = verify_mescom_r(driver, request.consumer_no)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))        
        
# ---------------------------------------------------------------

@app.post("/verify/uhbvn")
def verify_uhbvn_api(request: UHBVNRequest):
    with managed_driver() as driver:
        try:
            result = verify_uhbvn(driver, request.account_number)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))        
        
# ---------------------------------------------------------------

@app.post("/verify/dhbvn")
def verify_dhbvn_api(request: DHBVNRequest):
    with managed_driver() as driver:
        try:
            result = verify_dhbvn(driver, request.account_number)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))       
        
# ---------------------------RENT------------------------------------
@app.post("/verify/stamp_delhi")
def verify_delhi_stamp_api(request: DelhiStampDutyRequest):
    with managed_driver() as driver:
        try:
            result = verify_stamp_delhi(driver, request.certificate_no, request.state, request.stamp, request.certificate_issued_date, OPENAI_API_KEY)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# ---------------------------RENT------------------------------------
@app.post("/verify/stamp_gujrat")
def verify_gujrat_stamp_api(request: GujratStampDutyRequest):
    with managed_driver() as driver:
        try:
            result = verify_stamp_gujrat(driver, request.certificate_no, request.state, request.stamp, request.certificate_issued_date, OPENAI_API_KEY)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
# ---------------------------RENT------------------------------------
@app.post("/verify/stamp_karnatka")
def verify_karnatka_stamp_api(request: KarnatkaStampDutyRequest):
    with managed_driver() as driver:
        try:
            result = verify_stamp_karnatka(driver, request.certificate_no, request.state, request.stamp, request.certificate_issued_date, OPENAI_API_KEY)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))        
        
 # ---------------------------RENT------------------------------------
@app.post("/verify/stamp_rajasthan")
def verify_rajasthan_stamp_api(request: RajasthanStampDutyRequest):
    with managed_driver() as driver:
        try:
            result = verify_stamp_rajasthan(driver, request.certificate_no, request.state, request.stamp, request.certificate_issued_date, OPENAI_API_KEY)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))        
        
 # ---------------------------RENT------------------------------------
@app.post("/verify/stamp_punjab")
def verify_rajasthan_stamp_api(request: PunjabStampDutyRequest):
    with managed_driver() as driver:
        try:
            result = verify_stamp_punjab(driver, request.certificate_no, request.state, request.stamp, request.certificate_issued_date, OPENAI_API_KEY)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))                
        
 # ---------------------------RENT------------------------------------
@app.post("/verify/stamp_uttarpradesh")
def verify_uttarpradesh_stamp_api(request: UttarPradeshStampDutyRequest):
    with managed_driver() as driver:
        try:
            result = verify_stamp_uttarprdesh(driver, request.certificate_no, request.state, request.stamp, request.certificate_issued_date, OPENAI_API_KEY)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))                        


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)                 