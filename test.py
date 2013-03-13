import sys
import accBackend

print 'start'

oneBestList = ['good', 'bad']
refsList = [set(['good', 'great']), set(['difficult'])]
(correct, incorrect, acc) = accBackend.computeAccAt1(refsList, oneBestList)
print '{0} correct, {1} incorrect, {2} accuracy'.format(correct, incorrect, acc)

print 'end'
