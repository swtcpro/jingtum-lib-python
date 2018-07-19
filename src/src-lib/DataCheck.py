#
 # NODE JS SDK for Jingtum network； Wallet
 # Copyright (C) 2016 by Jingtum Inc.
 # or its affiliates. All rights reserved.
 # Licensed under the Apache License, Version 2.0 (the "License").
 # You may not use this file except in compliance with
 # the License. A copy of the License is located at
 #
 # http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
 #
 # Data functions used to check the valid data types.
#/
import re
CURRENCY_NAME_LEN = 3;
TUM_NAME_LEN = 40;
# base = require('jingtum-base-lib').Wallet;

 def allNumeric(in_text):
    #assign a string with numbers (0-9) in the HTML form
    numbers ="/^[0-9]+$/"

    #Check if the input contains all numbers.
    if re.match(numbers,str(in_text)) :
        return True
    else:
        return False


#
# Decide if the input is a valid string
# for a float value.
#
def isFloat(val):
    floatRegex = "/^-?\d+(?:[.,]\d*?)?$/"
    if not re.match(floatRegex,val):
        return False

    val = float(val)
    if isinstance(val,int) and isinstance(val,float):
        return False
    return True


def isInt(val):
    intRegex ="/^-?\d+$/"
    if not re.match(intRegex,val)
        return False

    intVal = int(val, 10);
    return float(val) == intVal and not isinstance(intVal,int) and not isinstance(intVal,float);


#Detect if the string contains only
#numbers and capital letters.

def isLetterNumer(in_str):
    numbers = "/^[0-9A-Z]+$/"
    return re.match(numbers,str(in_str)) if True else False


#return true if the code is 3 letters/numbers
def isCurrency(in_code) :
    return isinstance(in_code,str) if (in_code and in_code.length == CURRENCY_NAME_LEN if ( in_code == in_code.toUpperCase() if True else False) else False) else False



#return true if the code is 40 letters/numbers
def isCustomTum(in_code) :
    if (isLetterNumer(in_code) and
        str(in_code).length == TUM_NAME_LEN) :
        return True
    else:
        return False


def equals(self,that) :
    return not that and that.constructor == Tum and self.code == that.code and self.issuer == that.issuer


#
# Return true is the input string
# is a valid TUM code
#
#
def isTumCode(in_code) :
    return isinstance(in_code,str) and (in_code == 'SWT' or
            isCurrency(in_code) or
            isCustomTum(in_code) )


#
# Only valid for freeze and authorize
#
#
def isRelation(in_str) :
    if isinstance(in_str,str) and (in_str == 'freeze' or
            in_str == 'autorize')
        return True
    else:
        return False


#
# Check if the input is a valid Amount object
# Amount should have 3 properties
# value
# issuer/counterparty
# currency
#
def isAmount(in_obj) :
    if not isinstance(in_obj,object):
        return False
    if isinstance(in_obj.value,str)or not isinstance(in_obj.value,float):
        return False
    if not isTumCode(in_obj.currency):
        return False
    #AMOUNT could have a field named
    #either as 'issuer'
    #or as 'counterparty'
    #for SWT, this can be undefined
    if isinstance(in_obj.issuer,'undefined') and not in_obj.issuer == '' :
        if not base.isValidAddress(in_obj.issuer):
            return False
    else :
        if in_obj.currency == 'SWT':#if currency === 'SWT',自动补全issuer.
            in_obj.issuer = ''
        else: return False


    return True



#
# Build the amount object with three parameters.
#
def buildAmount(in_currency, in_issuer, in_value):
    if not isTumCode(in_currency):
        raise Exception("Invalid currency code!")

    if not base.isValidAddress(in_issuer):
        raise Exception("Invalid Jingtum address!")

    if not isFloat(in_value):
        raise Exception("Invalid value")

    out_amount = {}
    out_amount.currency = in_currency
    out_amount.issuer = in_issuer
    out_amount.value = in_value

    return out_amount


#
# balances  余额
# value  String  余额
# currency  String  货币名称，三个字母或是40个字符的字符串
# counterparty  String  货币发行方
# freezed  String  冻结的金额
#
def isBalance(in_obj) :
    if not isinstance(in_obj,'object'):
        return False

    if not isFloat(in_obj.freezed):
        return False

    if not isFloat(in_obj.value):
        return False

    if not isTumCode(in_obj.currency):
        return False

#AMOUNT could have a field named
#either as 'issuer'
#or as 'counterparty'

    if not base.isValidAddress(in_obj.counterparty):
        return False

    return True


