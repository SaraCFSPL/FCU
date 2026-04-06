from ..raj_stamp_duty_mapping import stamp_duty_display_names
from ..raj_stamp_duty import StampDutyType

def get_dropdown_options_raj():
 return [(code.value, stamp_duty_display_names[code]) for code in StampDutyType]

# Usage
dropdown_options = get_dropdown_options_raj()
for value, label in dropdown_options:
    (f"Value: {value} | Label: {label}")