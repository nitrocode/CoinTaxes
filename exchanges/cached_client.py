import os
from types import GeneratorType
import pickle

class CachedClient(object):

  def __init__(self, client_name, client_getter):
    self.__client_name      = client_name
    self.__client_getter    = client_getter
    self.__client_instance  = None
    self.__cache            = None


  # BEGIN OF public methods #
  """
  Write a cache file to disk
  """
  def cache_commit(self):
    cache_path = self.get_cache_file_path()
    cache_dir  = os.path.dirname(cache_path)
    if not os.path.exists(cache_dir):
      os.makedirs(cache_dir)
    if self.__cache != None:
      with open(cache_path, 'wb') as f:
        pickle.dump(self.__cache, f)
      print('Saved cache of %d entries for the exchange "%s"' % (len(self.__cache), self.__client_name) )
    return None

  """
  Calculate cache file path based on client name
  """
  def get_cache_file_path(self):
    cache_folder = 'cache'
    cache_path = cache_folder + '/' + self.__client_name + '.p'

    return cache_path
  # END OF public methods #

  """
  Intercepts access to client's methods and replaces them with proxy function 
  that returns cached data or calls a real method
  """
  def __getattr__(self, attr_name):
    # print("getattr(%s)" % (attr_name) )
    def proxy_fn(*args, **opts):
      # print("Proxied call to %s with args=%s and opts=%s" % (attr_name, args, opts) )
      # build cache key based on the attr name and parameter values
      key = self.__cache_calc_key(attr_name, args, opts)
      # look up key in the a cache file
      value = self.__cache_get(key)

      # if no data - ask real client and cache the response
      if value == None:
        value = self.__call_real_client(attr_name, args, opts)
        value = self.__unroll_value(value)
        self.__cache_set(key, value)

      return value
    
    # return proxy function
    return proxy_fn

  """
  Unroll generator values (e.g. paginated list of transactions) 
  into a regular list
  """
  def __unroll_value(self, value):
    if isinstance(value, GeneratorType):
      value = [ item for item in value ]

    return value

  """
  Calculates cache key by function name, positional arguments and keyword arguments
  """
  def __cache_calc_key(self, fn_name, args, opts):
    key_str = fn_name + '('

    for arg_idx, arg_value in enumerate(args):
      if arg_idx > 0:
        key_str += ', '
      key_str += str(arg_value)

    for opt_idx, opt_name in enumerate(opts):
      if opt_idx > 0 or len(args) > 0:
        key_str += ', '
      key_str += opt_name + '=' + str(opts[opt_name])

    key_str += ')'

    return key_str

  """
  Get a value from the cache
  """
  def __cache_get(self, key):
    # load cache if not loaded
    if self.__cache == None:
      self.__cache_load()

    if key not in self.__cache:
      return None

    return self.__cache[key]

  """
  Add/replace value in the cache
  """
  def __cache_set(self, key, value):
    if not isinstance(self.__cache, dict):
      self.__cache = {}
    
    self.__cache[key] = value

    return None
  
  """
  Read whole cache from a cache file into memory
  """
  def __cache_load(self):
    self.__cache = {}

    cache_path = self.get_cache_file_path()
    if os.path.exists(cache_path):
      with open(cache_path, 'rb') as f:
        self.__cache = pickle.load(f)
      print('Loaded cache of %d entries for the exchange "%s"' % (len(self.__cache), self.__client_name) )
    
    return None

  """
  Call a method of real client with provided arguments and options
  """
  def __call_real_client(self, fn_name, args, opts):
    if self.__client_instance == None:
      self.__client_instance = self.__client_getter()

    method = getattr(self.__client_instance, fn_name)
    
    return method(*args, **opts)


