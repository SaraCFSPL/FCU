from ..PB_stamp_duty_mapping import stamp_duty_display_names_punjab
from ..PB_stamp_duty import StampDutyTypePunjab

def get_dropdown_options_pb():
 return [(code.value, stamp_duty_display_names_punjab[code]) for code in StampDutyTypePunjab]

# Usage
dropdown_options = get_dropdown_options_pb()
for value, label in dropdown_options:
    (f"Value: {value} | Label: {label}")