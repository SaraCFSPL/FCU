from ..gj_stamp_duty_mapping import stamp_duty_display_names_gujarat
from ..gj_stamp_duty import StampDutyTypeGujarat

def get_dropdown_options_gj():
 return [(code.value, stamp_duty_display_names_gujarat[code]) for code in StampDutyTypeGujarat]

# Usage
dropdown_options = get_dropdown_options_gj()
for value, label in dropdown_options:
    (f"Value: {value} | Label: {label}")