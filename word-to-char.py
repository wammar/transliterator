import io
import sys
with io.open(sys.argv[1], encoding='utf8') as raw_file, io.open(sys.argv[2], encoding='utf8', mode='w') as split_file:
  for line in raw_file:
    chars = list(line.split()[0])
    split_file.write(' '.join(chars))
    split_file.write(u'\n')
