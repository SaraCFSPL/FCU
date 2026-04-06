from ..DL_stamp_duty import StampDutyTypeDL
from ..DL_stamp_duty_mapping import stamp_duty_display_names_DL

def get_dropdown_options_dl():
 return [(code.value, stamp_duty_display_names_DL[code]) for code in StampDutyTypeDL]

# Usage
get_dropdown_options_dl = get_dropdown_options_dl()
for value, label in get_dropdown_options_dl:
    (f"Value: {value} | Label: {label}")