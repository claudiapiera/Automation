
def prettyDict(d, indent=0):
   for key, value in d.items():
      print('\t' * indent + str(key))
      if isinstance(value, dict):
         prettyDict(value, indent+1)
      else:
         print('\t' * (indent+1) + str(value))

def writeDictIntoFile(intfs, filename):
    with open(filename, 'w') as f:
        for key, nested in sorted(intfs.items()):
            print(key, file=f)
            for subkey, value in sorted(nested.items()):
                print('   {}: {}'.format(subkey, value), file=f)
            print(file=f)