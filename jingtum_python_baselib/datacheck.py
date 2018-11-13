# Data functions used to check the valid data types.
import re

CURRENCY_NAME_LEN = 3
CURRENCY_NAME_LEN2 = 6
TUM_NAME_LEN = 40


# return True if the code is 3 letters/numbers
def is_currency(in_code):
    if isinstance(in_code, str):
        if in_code and len(in_code) >= CURRENCY_NAME_LEN and len(in_code) <= CURRENCY_NAME_LEN2:
            return True
        else:
            return False
    else:
        return False


# Detect if the string contains only
# numbers and capital letters.
def is_letter_numer(in_str):
    numbers = '^[0-9A-Z]+$'
    if re.match(numbers, str(in_str)):
        return True
    else:
        return False


# return True if the code is 40 letters/numbers
def is_custom_tum(in_code):
    if is_letter_numer(in_code) and \
    len(str(in_code)) == TUM_NAME_LEN:
        return True
    else:
        return False


# Return True is the input string
# is a valid TUM code
# input must be defined and non-null
# Make sure if the code meets the coding rule
# tum: Custom tum, 40 capital letters or number
def is_tum_code(in_code):
    return (isinstance(in_code,str) and \
        (in_code == 'SWT' or \
        is_currency(in_code) or \
        is_custom_tum(in_code)))