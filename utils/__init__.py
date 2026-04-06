from .solve_captcha import solve_tesseract_captcha
from .driver import setup_driver
from .extract_details import extract_gvcl_details_from_text
from .select_company import select_company
from .Stamp.DL_stamp_duty import StampDutyTypeDL
from .Stamp.DL_stamp_duty_mapping import stamp_duty_display_names_DL
from .Stamp.Dropdown.dropdown_dl import get_dropdown_options_dl
from .state import StateCode
from .Stamp.Dropdown.dropdown_gj import get_dropdown_options_gj
from .Stamp.gj_stamp_duty import StampDutyTypeGujarat
from .Stamp.gj_stamp_duty_mapping import stamp_duty_display_names_gujarat
from .Stamp.kar_stamp_duty import StampDutyTypeKarnataka
from .Stamp.kar_stamp_duty_mapping import stamp_duty_display_names_karnataka
from .Stamp.raj_stamp_duty import StampDutyType
from .Stamp.raj_stamp_duty_mapping import stamp_duty_display_names
from .Stamp.PB_stamp_duty import StampDutyTypePunjab
from .Stamp.PB_stamp_duty_mapping import stamp_duty_display_names_punjab
from .Stamp.up_stamp_duty_mapping import stamp_duty_display_names_uttarpradesh
from .Stamp.up_stamp_duty import StampDutyTypeUttarPradesh


__all__ = ["setup_driver",
           "solve_tesseract_captcha",
           "extract_gvcl_details_from_text",
           "select_company",
           "StampDutyTypeDL",
           "stamp_duty_display_names_DL",
           "get_dropdown_options_dl",
           "StateCode",
           'get_dropdown_options_gj',
           "StampDutyTypeGujarat",
           "stamp_duty_display_names_gujarat",
            'StampDutyTypeKarnataka',
            'stamp_duty_display_names_karnataka',
            'stamp_duty_display_names',
            'StampDutyType',
            'StampDutyTypePunjab',
            'stamp_duty_display_names_punjab',
            'stamp_duty_display_names_uttarpradesh',
            'StampDutyTypeUttarPradesh'
           
           ]
