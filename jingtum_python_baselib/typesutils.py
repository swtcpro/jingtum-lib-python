import math
import json
import re
from jingtum_python_baselib.utils import fmt_hex,hex_to_bytes,to_bytes
from jingtum_python_baselib.keypairs import decode_address
from jingtum_python_baselib.tum_amount import Amount

#Data type map.
# Mapping of type ids to data types. The type id is specified by the high
TYPES_MAP = [
    None,

    # Common
    'Int16',    # 1
    'Int32',    # 2
    'Int64',    # 3
    'Hash128',  # 4
    'Hash256',  # 5
    'Amount',   # 6
    'VL',       # 7
    'Account',  # 8

    # 9-13 reserved
    None,    # 9
    None,    # 10
    None,    # 11
    None,    # 12
    None,    # 13

    'Object',   # 14
    'Array',    # 15

    # Uncommon
    'Int8',     # 16
    'Hash160',  # 17
    'PathSet',  # 18
    'Vector256' # 19
]

# Field type map.
# Mapping of field type id to field type name.
FIELDS_MAP = {
    # Common types
    1: { # Int16
        1: 'LedgerEntryType',
        2: 'TransactionType'
    },
    2: { # Int32
        2: 'Flags',
        3: 'SourceTag',
        4: 'Sequence',
        5: 'PreviousTxnLgrSeq',
        6: 'LedgerSequence',
        7: 'CloseTime',
        8: 'ParentCloseTime',
        9: 'SigningTime',
        10: 'Expiration',
        11: 'TransferRate',
        12: 'WalletSize',
        13: 'OwnerCount',
        14: 'DestinationTag',
        # Skip 15
        16: 'HighQualityIn',
        17: 'HighQualityOut',
        18: 'LowQualityIn',
        19: 'LowQualityOut',
        20: 'QualityIn',
        21: 'QualityOut',
        22: 'StampEscrow',
        23: 'BondAmount',
        24: 'LoadFee',
        25: 'OfferSequence',
        26: 'FirstLedgerSequence',
        27: 'LastLedgerSequence',
        28: 'TransactionIndex',
        29: 'OperationLimit',
        30: 'ReferenceFeeUnits',
        31: 'ReserveBase',
        32: 'ReserveIncrement',
        33: 'SetFlag',
        34: 'ClearFlag',
        36: 'Method',
        39: 'Contracttype'
    },
    3: { # Int64
        1: 'IndexNext',
        2: 'IndexPrevious',
        3: 'BookNode',
        4: 'OwnerNode',
        5: 'BaseFee',
        6: 'ExchangeRate',
        7: 'LowNode',
        8: 'HighNode'
    },
    4: { # Hash128
        1: 'EmailHash'
    },
    5: { # Hash256
        1: 'LedgerHash',
        2: 'ParentHash',
        3: 'TransactionHash',
        4: 'AccountHash',
        5: 'PreviousTxnID',
        6: 'LedgerIndex',
        7: 'WalletLocator',
        8: 'RootIndex',
        9: 'AccountTxnID',
        16: 'BookDirectory',
        17: 'InvoiceID',
        18: 'Nickname',
        19: 'Amendment',
        20: 'TicketID'
    },
    6: { # Amount
        1: 'Amount',
        2: 'Balance',
        3: 'LimitAmount',
        4: 'TakerPays',
        5: 'TakerGets',
        6: 'LowLimit',
        7: 'HighLimit',
        8: 'Fee',
        9: 'SendMax',
        16: 'MinimumOffer',
        17: 'JingtumEscrow',
        18: 'DeliveredAmount'
    },
    7: { # VL
        1: 'PublicKey',
        2: 'MessageKey',
        3: 'SigningPubKey',
        4: 'TxnSignature',
        5: 'Generator',
        6: 'Signature',
        7: 'Domain',
        8: 'FundCode',
        9: 'RemoveCode',
        10: 'ExpireCode',
        11: 'CreateCode',
        12: 'MemoType',
        13: 'MemoData',
        14: 'MemoFormat',
        15: 'Payload',
        17: 'ContractMethod',
        18: 'Parameter'
    },
    8: { # Account
        1: 'Account',
        2: 'Owner',
        3: 'Destination',
        4: 'Issuer',
        7: 'Target',
        8: 'RegularKey'
    },
    14: { # Object
        1: None,  #end of Object
        2: 'TransactionMetaData',
        3: 'CreatedNode',
        4: 'DeletedNode',
        5: 'ModifiedNode',
        6: 'PreviousFields',
        7: 'FinalFields',
        8: 'NewFields',
        9: 'TemplateEntry',
        10: 'Memo',
        11: 'Arg'
    },
    15: { # Array
        1: None,  #end of Array
        2: 'SigningAccounts',
        3: 'TxnSignatures',
        4: 'Signatures',
        5: 'Template',
        6: 'Necessary',
        7: 'Sufficient',
        8: 'AffectedNodes',
        9: 'Memos',
        10: 'Args'
    },

    # Uncommon types
    16: { # Int8
        1: 'CloseResolution',
        2: 'TemplateEntryType',
        3: 'TransactionResult'
    },
    17: { # Hash160
        1: 'TakerPaysCurrency',
        2: 'TakerPaysIssuer',
        3: 'TakerGetsCurrency',
        4: 'TakerGetsIssuer'
    },
    18: { # PathSet
        1: 'Paths'
    },
    19: { # Vector256
        1: 'Indexes',
        2: 'Hashes',
        3: 'Amendments'
    }
}

# Inverse of the fields map
INVERSE_FIELDS_MAP = {
    'LedgerEntryType': [1, 1],
    'TransactionType': [1, 2],
    'Flags': [2, 2],
    'SourceTag': [2, 3],
    'Sequence': [2, 4],
    'PreviousTxnLgrSeq': [2, 5],
    'LedgerSequence': [2, 6],
    'CloseTime': [2, 7],
    'ParentCloseTime': [2, 8],
    'SigningTime': [2, 9],
    'Expiration': [2, 10],
    'TransferRate': [2, 11],
    'WalletSize': [2, 12],
    'OwnerCount': [2, 13],
    'DestinationTag': [2, 14],
    'HighQualityIn': [2, 16],
    'HighQualityOut': [2, 17],
    'LowQualityIn': [2, 18],
    'LowQualityOut': [2, 19],
    'QualityIn': [2, 20],
    'QualityOut': [2, 21],
    'StampEscrow': [2, 22],
    'BondAmount': [2, 23],
    'LoadFee': [2, 24],
    'OfferSequence': [2, 25],
    'FirstLedgerSequence': [2, 26],
    'LastLedgerSequence': [2, 27],
    'TransactionIndex': [2, 28],
    'OperationLimit': [2, 29],
    'ReferenceFeeUnits': [2, 30],
    'ReserveBase': [2, 31],
    'ReserveIncrement': [2, 32],
    'SetFlag': [2, 33],
    'ClearFlag': [2, 34],
    'Method': [2, 36],
    'Contracttype': [2, 39],
    'IndexNext': [3, 1],
    'IndexPrevious': [3, 2],
    'BookNode': [3, 3],
    'OwnerNode': [3, 4],
    'BaseFee': [3, 5],
    'ExchangeRate': [3, 6],
    'LowNode': [3, 7],
    'HighNode': [3, 8],
    'EmailHash': [4, 1],
    'LedgerHash': [5, 1],
    'ParentHash': [5, 2],
    'TransactionHash': [5, 3],
    'AccountHash': [5, 4],
    'PreviousTxnID': [5, 5],
    'LedgerIndex': [5, 6],
    'WalletLocator': [5, 7],
    'RootIndex': [5, 8],
    'AccountTxnID': [5, 9],
    'BookDirectory': [5, 16],
    'InvoiceID': [5, 17],
    'Nickname': [5, 18],
    'Amendment': [5, 19],
    'TicketID': [5, 20],
    'Amount': [6, 1],
    'Balance': [6, 2],
    'LimitAmount': [6, 3],
    'TakerPays': [6, 4],
    'TakerGets': [6, 5],
    'LowLimit': [6, 6],
    'HighLimit': [6, 7],
    'Fee': [6, 8],
    'SendMax': [6, 9],
    'MinimumOffer': [6, 16],
    'JingtumEscrow': [6, 17],
    'DeliveredAmount': [6, 18],
    'PublicKey': [7, 1],
    'MessageKey': [7, 2],
    'SigningPubKey': [7, 3],
    'TxnSignature': [7, 4],
    'Generator': [7, 5],
    'Signature': [7, 6],
    'Domain': [7, 7],
    'FundCode': [7, 8],
    'RemoveCode': [7, 9],
    'ExpireCode': [7, 10],
    'CreateCode': [7, 11],
    'MemoType': [7, 12],
    'MemoData': [7, 13],
    'MemoFormat': [7, 14],
    'Payload': [7, 15],
    'ContractMethod': [7, 17],
    'Parameter': [7, 18],
    'Account': [8, 1],
    'Owner': [8, 2],
    'Destination': [8, 3],
    'Issuer': [8, 4],
    'Target': [8, 7],
    'RegularKey': [8, 8],
    'undefined': [15, 1],
    'TransactionMetaData': [14, 2],
    'CreatedNode': [14, 3],
    'DeletedNode': [14, 4],
    'ModifiedNode': [14, 5],
    'PreviousFields': [14, 6],
    'FinalFields': [14, 7],
    'NewFields': [14, 8],
    'TemplateEntry': [14, 9],
    'Memo': [14, 10],
    'Arg': [14, 11],
    'SigningAccounts': [15, 2],
    'TxnSignatures': [15, 3],
    'Signatures': [15, 4],
    'Template': [15, 5],
    'Necessary': [15, 6],
    'Sufficient': [15, 7],
    'AffectedNodes': [15, 8],
    'Memos': [15, 9],
    'Args': [15, 10],
    'CloseResolution': [16, 1],
    'TemplateEntryType': [16, 2],
    'TransactionResult': [16, 3],
    'TakerPaysCurrency': [17, 1],
    'TakerPaysIssuer': [17, 2],
    'TakerGetsCurrency': [17, 3],
    'TakerGetsIssuer': [17, 4],
    'Paths': [18, 1],
    'Indexes': [19, 1],
    'Hashes': [19, 2],
    'Amendments': [19, 3]
}

# Convert an integer value into an array of bytes.
# The result is appended to the serialized object ('so').
def convert_integer_to_bytearray(val, bytes):
    if not isinstance(val,(int,float)):
        raise Exception('Value is not a number', bytes)

    if (val < 0 or val >= math.pow(256, bytes)):
        raise Exception('Value out of bounds')

    newBytes = []

    i = 0
    while i < bytes:
        newBytes.insert(0, val >> (i * 8) & 0xff)
        i += 1

    return newBytes



"""
 * return the transaction type in string
 * Data defined in the ledger entry:
  AccountRoot: [97].concat(sleBase,[
  Contract: [99].concat(sleBase,[
  DirectoryNode: [100].concat(sleBase,[
  EnabledFeatures: [102].concat(sleBase,[
  FeeSettings: [115].concat(sleBase,[
  GeneratorMap: [103].concat(sleBase,[
  LedgerHashes: [104].concat(sleBase,[
  Nickname: [110].concat(sleBase,[
  Offer: [111].concat(sleBase,[
  SkywellState: [114].concat(sleBase,[

  TODO: add string input handles
"""
def get_ledger_entry_type(structure):
    if isinstance(structure,int):
        if structure==97:
            output = 'AccountRoot'
        elif structure == 99:
            output = 'Contract'
        elif structure == 100:
            output = 'DirectoryNode'
        elif structure == 102:
            output = 'EnabledFeatures'
        elif structure == 115:
            output = 'FeeSettings'
        elif structure == 103:
            output = 'GeneratorMap'
        elif structure == 104:
            output = 'LedgerHashes'
        elif structure == 110:
            output = 'Nickname'
        elif structure == 111:
            output = 'Offer'
        elif structure == 114:
            output = 'SkywellState'
        else:
            raise Exception('Invalid input type for ransaction result!')
    elif isinstance(structure, str):
        if structure == 'AccountRoot':
            output = 97
        elif structure =='Contract':
            output = 99
        elif structure == 'DirectoryNode':
            output = 100
        elif structure == 'EnabledFeatures':
            output = 102
        elif structure == 'FeeSettings':
            output = 115
        elif structure == 'GeneratorMap':
            output = 103
        elif structure == 'LedgerHashes':
            output = 104
        elif structure == 'Nickname':
            output = 110
        elif structure == 'Offer':
            output = 111
        elif structure == 'SkywellState':
            output = 114
        else:
            output = 0#undefined results, should not come here.
    else:
        output = 'UndefinedLedgerEntry'
    #end typeof structure

    print('Get ledger entry type:', output)
    return output

# return the transaction type in string
# Data defined in the TRANSACTION_TYPES
def get_transaction_type(structure):
    if isinstance(structure, int):
        if structure == 0:
            output = 'Payment'
        elif structure == 3:
            output = 'AccountSet'
        elif structure == 5:
            output = 'SetRegularKey'
        elif structure == 7:
            output = 'OfferCreate'
        elif structure == 8:
            output = 'OfferCancel'
        elif structure == 9:
            output = 'Contract'
        elif structure == 10:
            output = 'RemoveContract'
        elif structure == 20:
            output = 'TrustSet'
        elif structure == 100:
            output = 'EnableFeature'
        elif structure == 101:
            output = 'SetFee'
        else:
            raise Exception('Invalid transaction type!')
    elif isinstance(structure, str):
        if structure == 'Payment':
            output = 0
        elif structure == 'AccountSet':
            output = 3
        elif structure == 'SetRegularKey':
            output = 5
        elif structure == 'OfferCreate':
            output = 7
        elif structure == 'OfferCancel':
            output = 8
        elif structure == 'Contract':
            output = 9
        elif structure == 'RemoveContract':
            output = 10
        elif structure == 'TrustSet':
            output = 20
        elif structure == 'EnableFeature':
            output = 100
        elif structure == 'SetFee':
            output = 101
        else:
            raise Exception('Invalid transaction type!')
    else:
        raise Exception('Invalid input type for transaction type!')
    #end typeof structure

    print('Get tx type:', output)
    return output

def convert_string_to_hex(inputstr):
    out_str = ""
    i = 0
    while i < len(str):
        out_str += (" 00" + str(int(ord(str[i]))))
        i += 1
    return out_str.upper()

class SerializedType:
    def serialize_varint(so, val):
        if (val < 0):
            raise Exception('Variable integers are unsigned.')

        if (val <= 192):
            so.append([val])
        elif (val <= 12480):
            val -= 193
            so.append([193 + (val >> 8), val & 0xff])
        elif (val <= 918744):
            val -= 12481
            so.append([241 + (val >> 16), val >> 8 & 0xff, val & 0xff])
        else:
            raise Exception('Variable integer overflow.')

# Input:  HEX data in string format
# Output: byte array
def serialize_hex(so, hexData, noLength=None):
    byteData = hex_to_bytes(hexData) #bytes.fromBits(hex.toBits(hexData))
    if not noLength:
        SerializedType.serialize_varint(so, len(byteData))
    so.append(byteData)

# used by Amount serialize
def array_set(count, value):
    a = []

    i = 0
    while i < count:
        a.append(value)
        i += 1

    return a

class STInt8(SerializedType):
    def serialize(so, val):
        so.buffer.extend(convert_integer_to_bytearray(val, 1))

class STInt16(SerializedType):
    def serialize(so, val):
        so.buffer.extend(convert_integer_to_bytearray(val, 2))

class STInt32(SerializedType):
    def serialize(so, val):
        so.buffer.extend(convert_integer_to_bytearray(val, 4))

# Use RegExp match function
# perform case-insensitive matching
# for HEX chars 0-9 and a-f
def isHexInt64String(val):
    return isinstance(val,str) and re.match('^[0-9A-F]{0,16}$i',val)

# Convert int64 big number input
# to HEX string, then serialize it.
# -2,147,483,648 to +2,147,483,648
class STInt64(SerializedType):
    def serialize888(so, val):
        if isinstance(val,(int,float)):
            val = math.floor(val)
            if (val < 0):
                raise Exception('Negative value for unsigned Int64 is invalid.')
            #bigNumObject = new BigInteger(String(val), 10)
            bn = val
            big_num_in_hex_str = hex(bn).replace('0x', '')
            # a = new BN('dead', 16)
            # b = new BN('101010', 2)
        elif isinstance(val,str):
            if not isHexInt64String(val):
                raise Exception('Not a valid hex Int64.')

            big_num_in_hex_str = val
        else:
            raise Exception('Invalid type for Int64')

        if len(big_num_in_hex_str) > 16:
            raise Exception('Int64 is too large')

        while len(big_num_in_hex_str) < 16:
            big_num_in_hex_str = '0' + big_num_in_hex_str

        serialize_hex(so, big_num_in_hex_str, True) #noLength = true

class STHash256:
    def serialize(so, val):
        if isinstance(val,str) and re.match('^[0-9A-F]{0,16}$i',val) \
            and len(val) <= 64:
            serialize_hex(so, val, True) #noLength = true
        else:
            raise Exception('Invalid Hash256')

class STHash160:
    def serialize(so, val):
        serialize_hex(so, hex_to_bytes(val), True)

class STCurrency:
    def serialize(so, val, swt_as_ascii):
        currencyData = val.to_bytes()
        if not currencyData:
            raise Exception('Tried to serialize invalid/unimplemented currency type.')
        so.append(currencyData)

class STAmount:
    def serialize(so, val):
        """"""
        amount = Amount.from_json(val)

        if (not amount.is_valid()):
            raise Exception('Not a valid Amount object.')

        # Amount(64 - bit integer)
        valueBytes = array_set(8, 0)

        # For SWT, offset is 0
        # only convert the value
        if amount.is_native():
            bn = amount._value
            valueHex = hex(bn).replace('0x', '')
            #print('valueHex is ',valueHex)

            # Enforce correct length (64 bits)
            if len(valueHex) > 16:
                raise Exception('Amount Value out of bounds')

            while len(valueHex) < 16:
                valueHex = '0' + valueHex

            # Convert the HEX value to bytes array
            valueBytes = hex_to_bytes(valueHex) # bytes.fromBits(hex.toBits(valueHex))

            # Clear most significant two bits - these bits should already be 0 if
            # Amount enforces the range correctly, but we'll clear them anyway just
            # so this code can make certain guarantees about the encoded value.
            valueBytes[0] &= 0x3f

            if not amount.is_negative():
                valueBytes[0] |= 0x40

            so.append(valueBytes)

        else:
            # For other non - native currency
            # 1.Serialize the currency value with offset
            # Put offset
            hi = 0
            lo = 0

            # First bit: non - native
            hi |= 1 << 31

            #print('amount._value is',amount._value)
            #print('amount._offset is', amount._offset)
            if (not amount.is_zero()):
                # Second bit: non - negative?
                if (not amount.is_negative()):
                    hi |= 1 << 30

                #print('amount._offset is',amount._offset)
                #print('amount._value is', amount._value)

                # Next eight bits: offset / exponent
                hi |= ((97 + amount._offset) & 0xff) << 22
                # Remaining 54 bits: mantissa
                hi |= amount._value >>32 & 0x3fffff
                lo = amount._value & 0xffffffff

            # Convert from a bitArray to an array of bytes.
            arr = [hi, lo]
            l = len(arr)

            if (l == 0):
                bl = 0
            else:
                x = arr[l - 1]
                bl = (l - 1) * 32 + (round(x / 0x10000000000) or 32)

            # Setup a new byte array and filled the byte data in
            # Results should not longer than 8 bytes as defined earlier
            tmparray = []

            i = 0
            while i < bl/8:
                if ((i & 3) == 0):
                    tmp = arr[round(i / 4)]
                #tmparray.append(tmp >> 24)
                tmparray.append((tmp >> 24) % 256)
                tmp <<= 8
                i += 1
            #print('tmparray is', tmparray)
            if len(tmparray) > 8:
                raise Exception('Invalid byte array length in AMOUNT value representation')
            valueBytes = tmparray

            so.append(valueBytes)

            # 2. Serialize the currency info with currency code
            # and issuer
            # console.log("Serial non-native AMOUNT ......")
            # Currency(160 - bit hash)
            tum_bytes = amount.tum_to_bytes()
            so.append(tum_bytes)

            # Issuer(160 - bit hash)
            # so.append(amount.issuer().to_bytes())
            so.append(decode_address(0,amount.issuer()))

class STVL(SerializedType):
    def serialize(so, val):
        if isinstance(val, str):
            serialize_hex(so, val)
        else:
            raise Exception('Unknown datatype.')

class STAccount(SerializedType):
    def serialize(so, val):
        byte_data = decode_address(0,val)
        SerializedType.serialize_varint(so, len(byte_data))
        so.append(byte_data)

class STArray(SerializedType):
    def serialize(so, val):
        i = 0
        l = len(val)
        while i < l:
            keys= list(val[0]) #TODO

            if len(keys) != 1:
                raise Exception('Cannot serialize an array containing non-single-key objects')

            field_name = keys[0]
            value = val[i][field_name]
            serialize(so, field_name, value)
            i += 1

        #Array ending marker
        STInt8.serialize(so, 0xf1)

class STPathSet(SerializedType):
    typeBoundary = 0xff
    typeEnd = 0x00
    typeAccount = 0x01
    typeCurrency = 0x10
    typeIssuer = 0x20
    def serialize(self, so, val):
        i = 0
        l = len(val)
        while i < l:
            # Boundary
            if (i):
                STInt8.serialize(so, self.typeBoundary)

            j = 0
            l2 = len(val[i])
            while j < l2:
                entry = val[i][j]
                #if (entry.hasOwnProperty('_value')) {entry = entry._value}
                type = 0

                if (entry.account):
                    type |= self.typeAccount
                if (entry.currency):
                    type |= self.typeCurrency
                if (entry.issuer):
                    type |= self.typeIssuer

                STInt8.serialize(so, type)

                if (entry.account):
                    #so.append(UInt160.from_json(entry.account).to_bytes())
                    so.append(decodeAddress(0,entry.account))

                if (entry.currency):
                    currencyBytes = STCurrency.from_json_to_bytes(entry.currency, entry.non_native)
                    so.append(currencyBytes)

                if (entry.issuer):
                    #so.append(UInt160.from_json(entry.issuer).to_bytes())
                    so.append(decode_address(0,entry.issuer))
                j += 1
            i += 1

        STInt8.serialize(so, self.typeEnd)

class STVector256(SerializedType):
    def serialize(so, val): #Assume val is an array of STHash256 objects.
        length_as_varint = SerializedType.serialize_varint(so, len(val) * 32)
        i = 0
        l = len(val)
        while i < l:
            STHash256.serialize(so, val[i])
            i += 1

class STMemo(SerializedType):
    def serialize(so, val, no_marker=None):
        keys = []

        for key in val:
            # Ignore lowercase field names - they're non-serializable fields by
            # convention.
            if key[0] == key[0].lower():
                return

            #Check the field
            if not INVERSE_FIELDS_MAP.__contains__(key):
                raise Exception('JSON contains unknown field: "' + key + '"')

            keys.append(key)

            # Sort fields
            keys = sort_fields(keys)

            # store that we're dealing with json
            isJson = (val.__contains__('MemoFormat') and val.MemoFormat == 'json')

            i = 0
            while i < len(keys):
                key = keys[i]
                value = val[key]
                if key == 'MemoType' or key == 'MemoFormat':
                    # MemoType and MemoFormat are always ASCII strings
                    value = convert_string_to_hex(value)
                    # MemoData can be a JSON object, otherwise it's a string
                elif key == 'MemoData':
                    if not isinstance(value,str):
                        if (isJson):
                            try:
                                value = convert_string_to_hex(json.stringify(value))
                            except Exception:
                                raise Exception('MemoFormat json with invalid JSON in MemoData field')
                        else:
                            raise Exception('MemoData can only be a JSON object with a valid json MemoFormat')
                    elif isinstance(value,str):
                        value = convert_string_to_hex(value)
                serialize(so, key, value)
                i += 1

            if (not no_marker):
                #Object ending marker
                STInt8.serialize(so, 0xe1)

def serialize(so, field_name, value):
    #so: a byte-stream to serialize into.
    #field_name: a string for the field name ('LedgerEntryType' etc.)
    #value: the value of that field.
    field_coordinates = INVERSE_FIELDS_MAP[field_name]
    type_bits = field_coordinates[0]
    field_bits = field_coordinates[1]

    if type_bits < 16:
        a= type_bits << 4
    else:
        a = 0
    if field_bits < 16:
        b = field_bits
    else:
        b = 0
    tag_byte = a|b

    if isinstance(value,str):
        if (field_name == 'LedgerEntryType'):
            values = get_ledger_entry_type(value)
        elif (field_name == 'TransactionResult'):
            values = get_transaction_type(value)#binformat.ter[value]

    STInt8.serialize(so, tag_byte)

    if (type_bits >= 16):
        STInt8.serialize(so, type_bits)

    if (field_bits >= 16):
        STInt8.serialize(so, field_bits)

    # Get the serializer class (ST...)
    if field_name == 'Memo' and isinstance(value,object):
        # for Memo we override the default behavior with our STMemo serializer
        serialized_object_type = 'STMemo'
    else:
        # for a field based on the type bits.
        serialized_object_type = 'ST'+ TYPES_MAP[type_bits]

    try:
        #print('so.buffer is', so.buffer)
        #print('value is', value)
        #print('field_name is', field_name)
        #print('call serialized_object_type',serialized_object_type)
        globals().get(serialized_object_type).serialize(so, value)
    except Exception:
        Exception(' (' + field_name + ')')



class STObject(SerializedType):
    def serialize(so, val, no_marker):
        keys = []
        for key in val:
            # Ignore lowerelif structure == field names - they're non-serializable fields by
            # convention.
            if key[0] == key[0].lower():
                return

            if not isinstance(INVERSE_FIELDS_MAP[key], list):
                raise Exception('JSON contains unknown field: "' + key + '"')

            keys.append(key)

        # Sort fields
        keys = sort_fields(keys)

        i = 0
        while i < len(keys):
            serialize(so, keys[i], val[keys[i]])
            i += 1

        if not no_marker:
            #Object ending marker
            STInt8.serialize(so, 0xe1)

def QuickSort(arr, firstIndex, lastIndex):
    if firstIndex < lastIndex:
        divIndex = Partition(arr, firstIndex, lastIndex)

        QuickSort(arr, firstIndex, divIndex)
        QuickSort(arr, divIndex + 1, lastIndex)
    else:
        return


def Partition(arr, firstIndex, lastIndex):
    i = firstIndex - 1
    for j in range(firstIndex, lastIndex):
        #if arr[j] <= arr[lastIndex]:
        if (sort_field_compare(arr[j],arr[lastIndex])<0):
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[lastIndex] = arr[lastIndex], arr[i + 1]
    return i


def sort_field_compare(a, b):
    a_field_coordinates = INVERSE_FIELDS_MAP[a]
    a_type_bits = a_field_coordinates[0]
    a_field_bits = a_field_coordinates[1]

    b_field_coordinates = INVERSE_FIELDS_MAP[b]
    b_type_bits = b_field_coordinates[0]
    b_field_bits = b_field_coordinates[1]

    # Sort by type id first, then by field id
    if a_type_bits != b_type_bits:
        return a_type_bits - b_type_bits
    else:
        return a_field_bits - b_field_bits

def sort_fields(keys):
    QuickSort(keys, 0, len(keys) - 1)
    return keys