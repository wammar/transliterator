import re
import time
import io
import sys
import argparse
from collections import defaultdict
import subprocess

# parse/validate arguments
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-cdec", help="cdec home", required=True)
arg_parser.add_argument("-transliterator", help="transliterator home", required=True)
arg_parser.add_argument("-labels", help="potential char mapping labels", 
                        required=True)
arg_parser.add_argument("-weights", help="feature weights zipped file (i.e. the trained transliteration model)", 
                        required=True)
arg_parser.add_argument("-oov", help="out-of-vocab file (one per line)", required=True)
arg_parser.add_argument("-kbest", type=int, default=100, help="number of candidate transliterations per OOV")
arg_parser.add_argument("-charlm", help="target character lm", required=True)
arg_parser.add_argument("-grammar", help="output cdec grammar with k transliterations for each oov", required=True)
args = arg_parser.parse_args()

# split oovs into characters
subprocess.call( [ 'python', 
                   '{}/word-to-char.py'.format(args.transliterator), 
                   args.oov,
                   '{}.char'.format(args.oov) ] )

# write ini file
ini_file = open('{}.ini'.format(args.oov), mode='w')
ini_file.write("formalism=scfg\n")
ini_file.write("grammar={}\n".format(args.labels))
ini_file.write("scfg_max_span_limit=1\n")
ini_file.write("feature_function=NgramFeatures -o 2 -U U01| -B B51| -S |\n")
ini_file.write("feature_function=RuleContextFeatures -t U08|%x[-1]|%x[0]|%y[0]\n")
ini_file.write("feature_function=RuleContextFeatures -t U09|%x[0]|%x[1]|%y[0]\n")
ini_file.write("feature_function=RuleContextFeatures -t U11|%x[-2]|%x[-1]|%x[0]|%y[0]\n")
ini_file.write("feature_function=RuleContextFeatures -t U12|%x[-1]|%x[0]|%x[1]|%y[0]\n")
ini_file.write("feature_function=RuleContextFeatures -t U13|%x[0]|%x[1]|%x[2]|%y[0]\n")                
ini_file.close()

# then use cdec to find the k-best transliterations of each oov
p = subprocess.Popen( [ '{}/decoder/cdec'.format(args.cdec),
                        '-c',
                        '{}.ini'.format(args.oov),
                        '-w',
                        args.weights,
                        '-i',
                        '{}.char'.format(args.oov),
                        '-k',
                        str(args.kbest) ],
                      stdout=subprocess.PIPE)
cdec_stdout = open('{}.cdecout'.format(args.oov), mode='w')
#cdec_stderr = open('{}.char.cdecerr'.format(args.oov), mode='w')
cdec_stdout.write(p.communicate()[0])
#cdec_stderr.write(p.communicate()[1])
cdec_stdout.close()
#cdec_stderr.close()

# then convert the labels into tokens
subprocess.call( ['python',
                  '{}/create-kbest-grammar.py'.format(args.transliterator), 
                  '-oov',
                  args.oov,
                  '-kbest',
                  '{}.cdecout'.format(args.oov),
                  '-clm',
                  args.charlm,
                  '-grammar',
                  args.grammar] )
