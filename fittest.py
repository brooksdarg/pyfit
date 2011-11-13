#!/usr/bin/env python

import sys
from fit import Fit

def main():

  try:
    file = sys.argv[1]
  except IndexError:
    file = None

  if file:
    ride = Fit(file)
    ride.Process()
  else:
    print 'Usage: %s file.fit' % sys.argv[0]

if __name__ == '__main__':
  main()
