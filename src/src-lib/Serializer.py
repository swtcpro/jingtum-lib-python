#
 # NODE JS SDK for Jingtum network.
 # @version 1.1.0
 # Copyright (C) 2016 by Jingtum Inc.
 #or its affiliates. All rights reserved.
 # Licensed under the Apache License, Version 2.0 (the "License").
 # You may not use self file except Exception as  in compliance with
 # the License. A copy of the License is located at
 #
 # http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable lawor agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either expressor implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.
 #
 # Serializer Class
 # Convert the input JSON format commands to
 # Hex value for local sign operation.
#
# assert = require('assert')
# extend = require('extend')
#
# stypes = require('./TypesUtils')
# hashjs = require('hash.js')
import hashlib
import copy
import json
REQUIRED = 0
OPTIONAL  = 1
DEFAULT =  2

base = [
    ['TransactionType', REQUIRED],
    ['Flags', OPTIONAL],
    ['SourceTag', OPTIONAL],
    ['LastLedgerSequence', OPTIONAL],
    ['Account', REQUIRED],
    ['Sequence', OPTIONAL],
    ['Fee', REQUIRED],
    ['OperationLimit', OPTIONAL],
    ['SigningPubKey', OPTIONAL],
    ['TxnSignature', OPTIONAL]
]

TRANSACTION_TYPES = {
    "AccountSet": [3].concat(base, [
        ['EmailHash', OPTIONAL],
        ['WalletLocator', OPTIONAL],
        ['WalletSize', OPTIONAL],
        ['MessageKey', OPTIONAL],
        ['Domain', OPTIONAL],
        ['TransferRate', OPTIONAL]
    ]),
    "TrustSet": [20].concat(base, [
        ['LimitAmount', OPTIONAL],
        ['QualityIn', OPTIONAL],
        ['QualityOut', OPTIONAL]
    ]),
    "OfferCreate": [7].concat(base, [
        ['TakerPays', REQUIRED],
        ['TakerGets', REQUIRED],
        ['Expiration', OPTIONAL]
    ]),
    "OfferCancel": [8].concat(base, [
        ['OfferSequence', REQUIRED]
    ]),
    "SetRegularKey": [5].concat(base, [
        ['RegularKey', REQUIRED]
    ]),
    "Payment": [0].concat(base, [
        ['Destination', REQUIRED],
        ['Amount', REQUIRED],
        ['SendMax', OPTIONAL],
        ['Paths', DEFAULT],
        ['InvoiceID', OPTIONAL],
        ['DestinationTag', OPTIONAL]
    ]),
    "Contract": [9].concat(base, [
        ['Expiration', REQUIRED],
        ['BondAmount', REQUIRED],
        ['StampEscrow', REQUIRED],
        ['JingtumEscrow', REQUIRED],
        ['CreateCode', OPTIONAL],
        ['FundCode', OPTIONAL],
        ['RemoveCode', OPTIONAL],
        ['ExpireCode', OPTIONAL]
    ]),
    "RemoveContract": [10].concat(base, [
        ['Target', REQUIRED]
    ]),
    "EnableFeature": [100].concat(base, [
        ['Feature', REQUIRED]
    ]),
    "SetFee": [101].concat(base, [
        ['Features', REQUIRED],
        ['BaseFee', REQUIRED],
        ['ReferenceFeeUnits', REQUIRED],
        ['ReserveBase', REQUIRED],
        ['ReserveIncrement', REQUIRED]
    ])
}

sleBase = [
    ['LedgerIndex', OPTIONAL],
    ['LedgerEntryType', REQUIRED],
    ['Flags', REQUIRED]
]

LEDGER_ENTRY_TYPES = {
    "AccountRoot": [97].concat(sleBase, [
        ['Sequence', REQUIRED],
        ['PreviousTxnLgrSeq', REQUIRED],
        ['TransferRate', OPTIONAL],
        ['WalletSize', OPTIONAL],
        ['OwnerCount', REQUIRED],
        ['EmailHash', OPTIONAL],
        ['PreviousTxnID', REQUIRED],
        ['AccountTxnID', OPTIONAL],
        ['WalletLocator', OPTIONAL],
        ['Balance', REQUIRED],
        ['MessageKey', OPTIONAL],
        ['Domain', OPTIONAL],
        ['Account', REQUIRED],
        ['RegularKey', OPTIONAL]]),
    "Contract": [99].concat(sleBase, [
        ['PreviousTxnLgrSeq', REQUIRED],
        ['Expiration', REQUIRED],
        ['BondAmount', REQUIRED],
        ['PreviousTxnID', REQUIRED],
        ['Balance', REQUIRED],
        ['FundCode', OPTIONAL],
        ['RemoveCode', OPTIONAL],
        ['ExpireCode', OPTIONAL],
        ['CreateCode', OPTIONAL],
        ['Account', REQUIRED],
        ['Owner', REQUIRED],
        ['Issuer', REQUIRED]]),
    "DirectoryNode": [100].concat(sleBase, [
        ['IndexNext', OPTIONAL],
        ['IndexPrevious', OPTIONAL],
        ['ExchangeRate', OPTIONAL],
        ['RootIndex', REQUIRED],
        ['Owner', OPTIONAL],
        ['TakerPaysCurrency', OPTIONAL],
        ['TakerPaysIssuer', OPTIONAL],
        ['TakerGetsCurrency', OPTIONAL],
        ['TakerGetsIssuer', OPTIONAL],
        ['Indexes', REQUIRED]]),
    "EnabledFeatures": [102].concat(sleBase, [
        ['Features', REQUIRED]]),
    "FeeSettings": [115].concat(sleBase, [
        ['ReferenceFeeUnits', REQUIRED],
        ['ReserveBase', REQUIRED],
        ['ReserveIncrement', REQUIRED],
        ['BaseFee', REQUIRED],
        ['LedgerIndex', OPTIONAL]]),
    "GeneratorMap": [103].concat(sleBase, [
        ['Generator', REQUIRED]]),
    "LedgerHashes": [104].concat(sleBase, [
        ['LedgerEntryType', REQUIRED],
        ['Flags', REQUIRED],
        ['FirstLedgerSequence', OPTIONAL],
        ['LastLedgerSequence', OPTIONAL],
        ['LedgerIndex', OPTIONAL],
        ['Hashes', REQUIRED]]),
    "Nickname": [110].concat(sleBase, [
        ['LedgerEntryType', REQUIRED],
        ['Flags', REQUIRED],
        ['LedgerIndex', OPTIONAL],
        ['MinimumOffer', OPTIONAL],
        ['Account', REQUIRED]]),
    "Offer": [111].concat(sleBase, [
        ['LedgerEntryType', REQUIRED],
        ['Flags', REQUIRED],
        ['Sequence', REQUIRED],
        ['PreviousTxnLgrSeq', REQUIRED],
        ['Expiration', OPTIONAL],
        ['BookNode', REQUIRED],
        ['OwnerNode', REQUIRED],
        ['PreviousTxnID', REQUIRED],
        ['LedgerIndex', OPTIONAL],
        ['BookDirectory', REQUIRED],
        ['TakerPays', REQUIRED],
        ['TakerGets', REQUIRED],
        ['Account', REQUIRED]]),
    "SkywellState": [114].concat(sleBase, [
        ['LedgerEntryType', REQUIRED],
        ['Flags', REQUIRED],
        ['PreviousTxnLgrSeq', REQUIRED],
        ['HighQualityIn', OPTIONAL],
        ['HighQualityOut', OPTIONAL],
        ['LowQualityIn', OPTIONAL],
        ['LowQualityOut', OPTIONAL],
        ['LowNode', OPTIONAL],
        ['HighNode', OPTIONAL],
        ['PreviousTxnID', REQUIRED],
        ['LedgerIndex', OPTIONAL],
        ['Balance', REQUIRED],
        ['LowLimit', REQUIRED],
        ['HighLimit', REQUIRED]])
}


METADATA = [
    ['TransactionIndex', REQUIRED],
    ['TransactionResult', REQUIRED],
    ['AffectedNodes', REQUIRED]
]

#defined results of transaction


#
 # convert a HEX to dec number
 # 0-9 to the same digit
 # a-f, A-F to 10 - 15,
 # all others to 0
#
def get_dec_from_hexchar(self,in_char):
    if in_char.length > 1:
        return 0
    asc_code = in_char.charCodeAt(0)
    if asc_code > 48:
        if asc_code < 58:
            #digit 1-9
            return asc_code - 48

        else:
            if asc_code > 64:
                if asc_code < 91:
                #letter A-F
                    return asc_code - 55
                else :
                    if asc_code > 96 and asc_code < 123:
                        return asc_code - 87




    return 0



#HEX string to bytes
#for a string, returns as byte array
#Input is not even, add 0 to the end.
#a0c -> a0 c0
def hex_str_to_byte_array(self,in_str):
    out = []
    str = in_str.replace("/\s|0x/g", "")
    for i in range(0,str.length,2):
        if i + 1 > str.length:
            out.append((get_dec_from_hexchar(str.charAt(i))) * 16)
        else:
            out.append((get_dec_from_hexchar(str.charAt(i))) * 16 + get_dec_from_hexchar(str.charAt(i + 1)))



def get_char_from_num(self,in_num):

    if in_num >= 0 and in_num < 10:
        return in_num + 48;#0-9
    if in_num >= 10 and in_num < 16:
        return in_num + 55;#A-F


#
 # Convert the byte array to HEX values as str
 # Input is 32-bits(byte) array
 # Output is String with ordered sequence of 16-bit values contains only 0-9 and A-F
#
def bytes_to_str(self,in_buf):
    #return sjcl.codec.hex.fromBits(self.to_bits()).toUpperCase()
    out = ""

    for i in range(0,in_buf.length):
        tmp = (in_buf[i] & 0xF0) >> 4

        if tmp >= 0 and tmp < 16:
            out += str.fromCharCode(get_char_from_num(tmp))

        tmp = in_buf[i] & 0x0F
        if tmp >= 0 and tmp < 16:
            out += str.fromCharCode(get_char_from_num(tmp))

    return out


#
 # buf is a byte array
 # pointer is an integer index of the buf
#
class Serializer():
    def __init__(self,buf):
        if isinstance(buf,[]) or isinstance(type(buf),bytes):
            self.buffer = buf
        elif isinstance(buf,str):
            self.buffer = hex_str_to_byte_array(buf);#sjcl.codec.bytes.fromBits(sjcl.codec.hex.toBits(buf))
        elif not buf:
            self.buffer = []
        else:
            raise Exception('Invalid buffer passed.')

        self.pointer = 0


    #
     # convert the input JSON to a byte array
     # as buffer
    #
    def from_json(self,obj):
        # Create a copy of the object so we don't modify the original one
        obj = copy.deepcopy(True, {}, obj)
        so = Serializer()
        if isinstance(obj['TransactionType'],int):
            obj['TransactionType'] = Serializer.lookup_type_tx(obj['TransactionType'])
            if not obj['TransactionType']:
                raise Exception('Transaction type ID is invalid.')



        if isinstance(obj['LedgerEntryType'],int):
            obj['LedgerEntryType'] = Serializer.lookup_type_le(obj['LedgerEntryType'])

            if not obj['LedgerEntryType']:
                raise Exception('LedgerEntryType ID is invalid.')



        if isinstance(obj['TransactionType'],str):
            typedef = TRANSACTION_TYPES[obj['TransactionType']]
            if not isinstance(typedef,[]):
                raise Exception('Transaction type is invalid')


            typedef = typedef.slice()
            obj['TransactionType'] = typedef.shift()
        elif isinstance(obj['LedgerEntryType'],str):
            typedef = LEDGER_ENTRY_TYPES[obj['LedgerEntryType']]

            if not isinstance(typedef,[]):
                raise Exception('LedgerEntryType is invalid')


            typedef = typedef.slice()
            obj['LedgerEntryType'] = typedef.shift()

        elif isinstance(obj['AffectedNodes'],'object'):
            typedef = METADATA;#binformat
        else:
            raise Exception('Object to be serialized must contain either' +
                ' TransactionType, LedgerEntryType or AffectedNodes.')

        so.serialize(typedef, obj)

        return so


    # #
    #  # Use TRANSACTION_TYPES info to check if the input
    #  # TX missing any info
    # #
    # def check_no_missing_fields(typedef, obj):
    #     missing_fields = []
    #
    #     for i in range(typedef.length-1,0,-1):
    #         spec = typedef[i]
    #         field = spec[0]
    #         requirement = spec[1]
    #         # console.log("check missing:", spec);
    #
    #         if REQUIRED is requirement and obj[field] is None:
    #             missing_fields.append(field)
    #
    #
    #
    #     if missing_fields.length > 0:
    #
    #
    #         if obj.TransactionType is not None:
    #             object_name = Serializer.lookup_type_tx(obj.TransactionType)
    #         elif not obj.LedgerEntryType:
    #             object_name = Serializer.lookup_type_le(obj.LedgerEntryType)
    #         else:
    #             object_name = "TransactionMetaData"
    #
    #
    #         raise Exception(object_name + " is missing fields: " +
    #             json.dumps(missing_fields))
    #
    #
    #
    # #
    #  # Append the input bytes array to
    #  # the internal buffer and set the pointer
    #  # to the end.
    # #
    # def append(self,bytes):
    #     if isinstance(bytes,Serializer):
    #         bytes = bytes.buffer
    #
    #
    #     self.buffer = self.buffer.concat(bytes)
    #     self.pointer += bytes.length
    #
    #
    # def resetPointer(self):
    #     self.pointer = 0
    #
    #
    # def read(self,bytes):
    #         start = self.pointer
    #         end = start + bytes
    #
    #         # console.log("buffer len", self.buffer.length);
    #         if end > self.buffer.length:
    #             raise Exception('Buffer length exceeded')
    #
    #
    #         result = self.buffer.slice(start, end)
    #
    #         self.pointer = end
    #
    #
    #         return result
    #
    #
    # def peek(self, bytes):
    #     start = self.pointer
    #     end = start + bytes
    #
    #     # console.log("buffer len", self.buffer.length);
    #     if end > self.buffer.length:
    #         raise Exception('Buffer length exceeded')
    #
    #     result = self.buffer.slice(start, end)
    #
    #
    #     return result
    #
    #
    #
    # #
    #  # Convert the byte array to HEX values
    # #
    # def to_hex(self):
    #     return self.bytes_to_str(self.buffer)
    #
    #

    # #
    #  # Convert the byte array to JSON format
    # #
    # def to_json(self):
    #     old_pointer = self.pointer
    #     self.resetPointer()
    #     output = {}
    #
    #     while self.pointer < self.buffer.length:
    #         #Get the bytes array for the right Serialize type.
    #         key_and_value = stypes.parse(self)
    #         key = key_and_value[0]
    #         value = key_and_value[1]
    #
    #         output[key] = Serializer.jsonify_structure(value, key)
    #
    #
    #     self.pointer = old_pointer
    #
    #     return output
    #


    # #
    #  # Conver the input data structure to JSON format
    #  # function
    #  # object
    #  # array
    #  #
    # #
    # def jsonify_structure(self,structure, field_name):
    #     # console.log("jsonify_structure", typeof structure, field_name);
    #     if isinstance(structure,'number'):
    #         if(field_name=='LedgerEntryType'):
    #             output = stypes.get_ledger_entry_type(structure); # TODO: REPLACE, return string
    #         elif(field_name=='TransactionResult'):
    #             output = stypes.get_transaction_result(structure); # TRANSACTION_RESULTS[structure]; // TODO: REPLACE, return string
    #         elif(field_name=='TransactionType'):
    #             output = stypes.get_transaction_type(structure); # TRANSACTION_TYPES[structure]
    #         else:
    #             output = structure
    #     elif structure and isinstance(structure,'object'):
    #         if isinstance(structure.to_json,'function'):
    #             output = structure.to_json()
    #         else:
    #             # new Array or Object
    #             output = structure.constructor()
    #
    #             keys = object.keys(structure)
    #
    #             for i in range(0,keys.length):
    #                 key = keys[i]
    #                 output[key] = Serializer.jsonify_structure(structure[key], key)
    #     else:
    #         output = structure
    #     return output
    #
    #
    # #
    #  # Serialize the object
    # #
    # def serialize(self,typedef, obj) :
    #     # Serialize object without end marker
    #     stypes.Object.serialize(self, obj, True)
    #
    #
    #
    #
    # #
    #  # Hash data using SHA-512 and return the first 256 bits
    #  # in HEX string format.
    # #
    # def hash(self,prefix):
    #     sign_buffer = Serializer()
    #     # Add hashing prefix
    #     if isinstance(prefix,"undefined"):
    #         stypes.Int32.serialize(sign_buffer, prefix)
    #
    #     # Copy buffer to temporary buffer
    #     sign_buffer.append(self.buffer)
    #     # console.log("\nSign :", self.bytes_to_str(sign_buffer.buffer));
    #     return self.bytes_to_str(hashlib.sha512().update(sign_buffer.buffer).digest().slice(0, 32))
    #
    #
    #
    # def get_field_header(self,type_id, field_id):
    #     buffer = [0]
    #
    #     if type_id > 0xF:
    #         buffer.append(type_id & 0xFF)
    #     else:
    #         buffer[0] += (type_id & 0xF) << 4
    #
    #
    #     if field_id > 0xF:
    #         buffer.append(field_id & 0xFF)
    #     else:
    #         buffer[0] += field_id & 0xF
    #
    #
    #     return buffer
    #

    # #
    #  # Sort the input cmd according to
    #  # the TX type code.
    # #
    # def sort_typedef(self,typedef):
    #     assert(type(typedef),[])
    #     _sort_field_compare(a,b)
    #
    # def _sort_field_compare(self,a, b):
    #         # Sort by type id first, then by field id
    #     return a[3] is not b[3] if stypes[a[3]].id - stypes[b[3]].id else a[2] - b[2]
    #
    #
    #     return typedef.sort(sort_field_compare)
    #
    #
    # def lookup_type_tx(self,id):
    #     self.assertAlmostEqual(type(id),'number')
    #     return TRANSACTION_TYPES[id]
    #
    #
    # def lookup_type_le(self,id):
    #     self.assertEqual(type(id),'number')
    #     return LEDGER_ENTRY_TYPES[id]

