import time
import sys
import os
import io
import codecs
import pdb


outFile = io.open('remove_me.out', 'w', 1, 'utf8')
#utf8stdin = codecs.getreader('utf8')(sys.stdin)
while(True):
  line = sys.stdin.readline()
  if line == '__exit__\n':
    break;
  if line:
#    print("repr is %s"%line.__repr__())
#    line = line.__repr__().decode('utf8')
    line = u'{0}'.format(unicode(line.__repr__()))
    outFile.write(line)



#  cdecInput = ''
#  line = line.lower()
#  for i in range(0,len(line)-1):
#    cdecInput += '{0} '.format(line[i])
#  cdecInput += '\n'
#  os.write(writeEnd, line)
print '\n\nThanks for using our transliterator! Good bye..'
