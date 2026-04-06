from ..up_stamp_duty_mapping import stamp_duty_display_names_uttarpradesh
from ..up_stamp_duty import StampDutyTypeUttarPradesh

def get_dropdown_options_up():
 return [(code.value, stamp_duty_display_names_uttarpradesh[code]) for code in StampDutyTypeUttarPradesh]

# Usage
dropdown_options = get_dropdown_options_up()
for value, label in dropdown_options:
    (f"Value: {value} | Label: {label}")