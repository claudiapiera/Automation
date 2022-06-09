import pickle

def prettyDict(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         prettyDict(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

def readPickleFile(filename):
   with open(filename, 'rb') as handle:
      b = pickle.load(handle)
   return b

def writePickleFile(content, filename):
   with open(filename, 'wb') as handle:
      pickle.dump(content, handle, protocol=pickle.HIGHEST_PROTOCOL)
