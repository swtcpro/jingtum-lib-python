"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/5/1
 * Time: 12:29
 * Description: 
"""
import json
import os


class ConfigException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Config(object):
    path = os.path.split(os.path.realpath(__file__))[0]
    f = open(path + '/config.json')
    ff = f.read()
    config = json.loads(ff)
    f.close()

    try:
        CURRENCY_TYPE = config["constant"]["currency_type"]
        TRAN_PERFIX = config["constant"]["tran_perfix"]
        TRUST_LIMIT = config["constant"]["trust_limit"]
        SIGN_PREFIX = config["constant"]["sign_perfix"]
        MIN_ACTIVE_AMT = config["constant"]["min_active_amt"]
        SDK_VERSION = config["constant"]["sdk_version"]
        FEE = config["constant"]["fee"]
        currency = config["constant"]["currency"]
        issue_custom_tum = config["constant"]["issue_custom_tum"]
        query_issue = config["constant"]["query_issue"]
        query_custom_tum = config["constant"]["query_custom_tum"]

        sdk_api_address = config["prod"]["api_address"]
        sdk_web_socket_address = config["prod"]["web_socket_address"]
        sdk_api_version = config["prod"]["api_version"]
        ttong_address = config["prod"]["ttong_address"]

        test_api_address = config["dev"]["api_address"]
        test_web_socket_address = config["dev"]["web_socket_address"]
        test_api_version = config["dev"]["api_version"]
        test_ttong_address = config["dev"]["ttong_address"]
    except:
        raise ConfigException("config.json error")
