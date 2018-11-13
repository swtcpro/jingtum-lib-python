# Serializer Class
# Convert the input JSON format commands to
# Hex value for local sign operation.

import hashlib
import copy
import json
from jingtum_python_baselib.utils import to_bytes,fmt_hex,bytes_to_hex
from jingtum_python_baselib.typesutils import *
from jingtum_python_baselib.keypairs import hash512

REQUIRED = 0
OPTIONAL = 1
DEFAULT = 2

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
    "AccountSet": [[3] + base +
        [['EmailHash', OPTIONAL],
        ['WalletLocator', OPTIONAL],
        ['WalletSize', OPTIONAL],
        ['MessageKey', OPTIONAL],
        ['Domain', OPTIONAL],
        ['TransferRate', OPTIONAL]]],
    "TrustSet": [[20] + base +
        [['LimitAmount', OPTIONAL],
        ['QualityIn', OPTIONAL],
        ['QualityOut', OPTIONAL]]
    ],
    "RelationSet": [[21] + base +
        [['Target', REQUIRED],
        ['RelationType', REQUIRED],
        ['LimitAmount', OPTIONAL]]
    ],
    "RelationDel": [[22] + base +
        [['Target', REQUIRED],
        ['RelationType', REQUIRED],
        ['LimitAmount', OPTIONAL]]
    ],
    "OfferCreate": [[7] + base +
        [['TakerPays', REQUIRED],
        ['TakerGets', REQUIRED],
        ['Expiration', OPTIONAL]]
    ],
    "OfferCancel": [[8] + base +
        [['OfferSequence', REQUIRED]]
    ],
    "SetRegularKey": [[5] + base +
        [['RegularKey', REQUIRED]]
    ],
    "Payment": [[0] + base +
        [['Destination', REQUIRED],
        ['Amount', REQUIRED],
        ['SendMax', OPTIONAL],
        ['Paths', DEFAULT],
        ['InvoiceID', OPTIONAL],
        ['DestinationTag', OPTIONAL]]
    ],
    "Contract": [[9] + base +
        [['Expiration', REQUIRED],
        ['BondAmount', REQUIRED],
        ['StampEscrow', REQUIRED],
        ['JingtumEscrow', REQUIRED],
        ['CreateCode', OPTIONAL],
        ['FundCode', OPTIONAL],
        ['RemoveCode', OPTIONAL],
        ['ExpireCode', OPTIONAL]]
    ],
    "RemoveContract": [[10] + base +
        [['Target', REQUIRED]]
    ],
    "EnableFeature": [[100] + base +
        [['Feature', REQUIRED]]
    ],
    "SetFee": [[101] + base +
        [['Features', REQUIRED],
        ['BaseFee', REQUIRED],
        ['ReferenceFeeUnits', REQUIRED],
        ['ReserveBase', REQUIRED],
        ['ReserveIncrement', REQUIRED]]
    ],
    'ConfigContract': [[30] + base + [
        ['Method', REQUIRED],
        ['Payload', OPTIONAL],
        ['Destination', OPTIONAL],
        ['Amount', OPTIONAL],
        ['Contracttype', OPTIONAL],
        ['ContractMethod', OPTIONAL],
        ['Args', OPTIONAL]]
    ]
}

sleBase = [
    ['LedgerIndex', OPTIONAL],
    ['LedgerEntryType', REQUIRED],
    ['Flags', REQUIRED]
]

LEDGER_ENTRY_TYPES = {
    "AccountRoot": [[97] + sleBase +
        [['Sequence', REQUIRED],
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
        ['RegularKey', OPTIONAL]]
    ],
    "Contract": [[99] + sleBase +
        [['PreviousTxnLgrSeq', REQUIRED],
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
        ['Issuer', REQUIRED]]],
    "DirectoryNode": [[100] + sleBase +
        [['IndexNext', OPTIONAL],
        ['IndexPrevious', OPTIONAL],
        ['ExchangeRate', OPTIONAL],
        ['RootIndex', REQUIRED],
        ['Owner', OPTIONAL],
        ['TakerPaysCurrency', OPTIONAL],
        ['TakerPaysIssuer', OPTIONAL],
        ['TakerGetsCurrency', OPTIONAL],
        ['TakerGetsIssuer', OPTIONAL],
        ['Indexes', REQUIRED]]],
    "EnabledFeatures": [[102] + sleBase +
        [['Features', REQUIRED]]],
    "FeeSettings": [115] + sleBase +
        [['ReferenceFeeUnits', REQUIRED],
        ['ReserveBase', REQUIRED],
        ['ReserveIncrement', REQUIRED],
        ['BaseFee', REQUIRED],
        ['LedgerIndex', OPTIONAL]],
    "GeneratorMap": [[103] + sleBase +
        [['Generator', REQUIRED]]],
    "LedgerHashes": [[104] + sleBase +
        [['LedgerEntryType', REQUIRED],
        ['Flags', REQUIRED],
        ['FirstLedgerSequence', OPTIONAL],
        ['LastLedgerSequence', OPTIONAL],
        ['LedgerIndex', OPTIONAL],
        ['Hashes', REQUIRED]]],
    "Nickname": [[110] + sleBase,
        [['LedgerEntryType', REQUIRED],
        ['Flags', REQUIRED],
        ['LedgerIndex', OPTIONAL],
        ['MinimumOffer', OPTIONAL],
        ['Account', REQUIRED]]],
    "Offer": [[111] + sleBase +
        [['LedgerEntryType', REQUIRED],
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
        ['Account', REQUIRED]]],
    "SkywellState": [[114] + sleBase +
        [['LedgerEntryType', REQUIRED],
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
        ['HighLimit', REQUIRED]]]
}


METADATA = [
    ['TransactionIndex', REQUIRED],
    ['TransactionResult', REQUIRED],
    ['AffectedNodes', REQUIRED]
]


# convert a HEX to dec number
# 0-9 to the same digit
# a-f, A-F to 10 - 15,
# all others to 0
def get_dec_from_hexchar(self,in_char):
    if len(in_char) > 1:
        return 0
    asc_code = in_char.charCodeAt(0)
    if asc_code > 48:
        if asc_code < 58:
            # digit 1-9
            return asc_code - 48

        else:
            if asc_code > 64:
                if asc_code < 91:
                    # letter A-F
                    return asc_code - 55
                else:
                    if asc_code > 96 and asc_code < 123:
                        return asc_code - 87

    return 0


# HEX string to bytes
# for a string, returns as byte array
# Input is not even, add 0 to the end.
# a0c -> a0 c0
def hex_str_to_byte_array(self, in_str):
    out = []
    str = in_str.replace("/\s|0x/g", "")
    for i in range(0,len(str),2):
        if i + 1 > len(str):
            out.append((get_dec_from_hexchar(str[i])) * 16)
        else:
            out.append((get_dec_from_hexchar(str[i])) * 16 + get_dec_from_hexchar(str[i + 1]))


def sort_fields(keys):
    def sort_key(a):
        type_bits, field_bits = INVERSE_FIELDS_MAP[a]
        return type_bits, field_bits
    keys = keys[:]
    keys.sort(key=sort_key)
    return keys


def get_char_from_num(in_num):
    if (in_num >= 0 and in_num < 10):
        return in_num + 48 #0-9
    if (in_num >= 10 and in_num < 16):
        return in_num + 55 #A-F


# buf is a byte array
# pointer is an integer index of the buf
class Serializer:
    def __init__(self,buf):
        if isinstance(buf, dict) or isinstance(type(buf),bytes):
            self.buffer = buf
        elif isinstance(buf,str):
            self.buffer = hex_str_to_byte_array(buf)  # no use here
        elif not buf:
            self.buffer = []
        else:
            raise Exception('Invalid buffer passed.')

        self.pointer = 0

    # Serialize the object
    def serialize(self, typedef, obj):
        # Serialize object without end marker
        STObject.serialize(self, obj, True)

    def lookup_type_tx(id):
        return TRANSACTION_TYPES[id]

    def lookup_type_le(id):
        return LEDGER_ENTRY_TYPES[id]

    # convert the input JSON to a byte array
    # as buffer
    def from_json(self,obj):
        # Create a copy of the object so we don't modify the original one
        obj = copy.deepcopy(obj)
        so = Serializer(None)
        if isinstance(obj['TransactionType'],int):
            obj['TransactionType'] = Serializer.lookup_type_tx(obj['TransactionType'])
            if not obj['TransactionType']:
                raise Exception('Transaction type ID is invalid.')

        if obj.__contains__('LedgerEntryType'):
            if isinstance(obj['LedgerEntryType'],int):
                obj['LedgerEntryType'] = Serializer.lookup_type_le(obj['LedgerEntryType'])

                if not obj['LedgerEntryType']:
                    raise Exception('LedgerEntryType ID is invalid.')

        if isinstance(obj['TransactionType'],str):
            typedef = copy.deepcopy(TRANSACTION_TYPES[obj['TransactionType']][0])
            if not isinstance(typedef,list):
                raise Exception('Transaction type is invalid')

            obj['TransactionType'] = typedef.pop(0)
        elif isinstance(obj['LedgerEntryType'],str):
            typedef = copy.deepcopy(LEDGER_ENTRY_TYPES[obj['LedgerEntryType']][0])

            if not isinstance(typedef,list):
                raise Exception('LedgerEntryType is invalid')

            obj['LedgerEntryType'] = typedef.pop(0)

        elif isinstance(obj['AffectedNodes'],object):
            typedef = METADATA  # binformat
        else:
            raise Exception('Object to be serialized must contain either' +
                ' TransactionType, LedgerEntryType or AffectedNodes.')

        so.serialize(typedef, obj)

        return so

    def to_hex(self):
        return bytes_to_hex(self.buffer)

    # Append the input bytes array to
    # the internal buffer and set the pointer
    # to the end.
    def append(self, input_bytes):
        if isinstance(input_bytes, Serializer):
            input_bytes = input_bytes.buffer

        self.buffer.extend(input_bytes)

    # Hash data using SHA - 512 and return the first 256 bits
    # in HEX string format.
    def hash(self, prefix):
        sign_buffer = Serializer(None)
        # Add hashing prefix
        if prefix is not None:
            STInt32.serialize(sign_buffer, prefix)
        # Copy buffer to temporary buffer
        sign_buffer.append(self.buffer)
        return bytes_to_hex(hash512(bytearray(sign_buffer.buffer))[0:32])