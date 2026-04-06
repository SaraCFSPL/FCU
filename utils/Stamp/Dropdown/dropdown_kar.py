from ..kar_stamp_duty_mapping import stamp_duty_display_names_karnataka
from ..kar_stamp_duty import StampDutyTypeKarnataka

def get_dropdown_options_kar():
 return [(code.value, stamp_duty_display_names_karnataka[code]) for code in StampDutyTypeKarnataka]

# Usage
dropdown_options = get_dropdown_options_kar()
for value, label in dropdown_options:
    (f"Value: {value} | Label: {label}")