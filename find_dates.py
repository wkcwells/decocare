
import sys
import argparse
import textwrap

from pprint import pprint, pformat
from binascii import hexlify
from datetime import datetime

from decocare import lib
from decocare.records import times

def get_opt_parser( ):
  parser = argparse.ArgumentParser( )
  parser.add_argument('infile', nargs="+",
                      default=sys.stdin,
                      type=argparse.FileType('r'),
                      help="Find dates in this file.")

  parser.add_argument('--out',
                      default=sys.stdout,
                      type=argparse.FileType('w'),
                      help="Write records here.")
  return parser

def find_dates(stream):
  records = [ ]
  bolus = bytearray(stream.read(4))
  dates = [ ]
  extra = bytearray( )
  everything = bolus
  opcode = ''
  last = 0
  for B in iter(lambda: stream.read(1), ""):
    h, t = B[:1], B[1:]
    bolus.append(h)
    bolus.extend(t)
    everything.extend(B)
    if len(everything) < 5:
      continue
    candidate = everything[-5:]
    date = times.parse_date(candidate)
    if date is not None:
      last = stream.tell( )
      # last = len(everything)
      start = last - 5
      print "### FOUND ", date.isoformat( ), ' @ ', start, "%#08x" % start
      print "#### previous"
      print lib.hexdump(bolus, indent=4)
      print "#### datetime"
      print lib.hexdump(candidate, indent=4)
      print ""
      found = dict(timestamp=date, blob=bolus)
      # print lib.hexdump(bolus)
      records.append(found)
      bolus = bytearray( )
  return records

def main( ):
  parser = get_opt_parser( )
  opts = parser.parse_args( )
  tw_opts = {
    'width': 50,
    'subsequent_indent': '          ',
    'initial_indent': '       ',
  }
  wrapper = textwrap.TextWrapper(**tw_opts)
  for stream in opts.infile:
    find_dates(stream)

if __name__ == '__main__':
  main( )
#####
# EOF
