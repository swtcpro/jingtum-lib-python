"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/6/15
 * Time: 0:27
 * Description: 
"""
import unittest

from src.logger import logger
from src.remote import Remote


class RemoteTest(unittest.TestCase):

    def test_server_info(self):
        remote = Remote()
        if not isinstance(remote.connect(None), Exception):
            req = remote.request_server_info()
            result = remote.parse_server_info(req.submit())
            logger.info(result)


if __name__ == '__main__':
    unittest.main()
