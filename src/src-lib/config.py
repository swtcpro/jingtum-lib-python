# This object serves as a singleton to store config options

# var extend = require('extend')
import copy

class Config(object):
  def load(self,newOpts):
    copy.deepcopy(self,newOpts)
    return self
config=Config()