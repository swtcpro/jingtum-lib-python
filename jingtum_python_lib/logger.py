
"""
 * Created with PyCharm.
 * User: 彭诗杰
 * Date: 2018/5/1
 * Time: 13:11
 * Description:
"""

import logging
import sys
 

def set_logger(level=logging.DEBUG, path=sys.path[0], name="jingtumsdk.log"):
   logger = logging.getLogger() 
   logger.setLevel(level)  
   fh = logging.FileHandler(path + '/' + name)  
   ch = logging.StreamHandler() 

   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
   fh.setFormatter(formatter)  
   ch.setFormatter(formatter)  

   logger.addHandler(fh)  
   logger.addHandler(ch) 

   return logger

logger = set_logger()

