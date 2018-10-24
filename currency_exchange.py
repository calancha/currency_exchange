#!/usr/bin/env python2
import urllib2
import sys
import json
import getopt

class CurrencyExchange(object):
  """
  Retrieve current exchange betwee currency couples.
  """
  def __init__(self, *args):
    self.api_key = None
    self.debug = False
    self.currency_pairs = []
    self.uri_end_point = "https://forex.1forge.com/1.0.3/quotes"

    self.output_file = None
    self.include_csv_headers = False
    self.parse_arguments(list(args))

    if self.debug:
      print "[DEBUG] Will retrieve currency exchanges: '%s'" %','.join(self.currency_pairs)
      print "[DEBUG] Using API key: '%s'" %self.api_key
      if self.output_file:
        print "[DEBUG] Write output to: '%s'" %self.output_file
        if self.include_csv_headers:
          print "[DEBUG] Include header in csv file"

  def parse_arguments(self, args):
    if not args:
      usage()
      sys.exit(0)
    try:
      long_options = ['help', 'pairs=', 'api_key=', 'debug', 'include-csv-headers']
      opts, positional_args = getopt.gnu_getopt(args, 'hp:k:di', long_options)
    except getopt.GetoptError as err:
      user_error(str(err))
    for opt, arg in opts:
      if opt in ['-h', '--help']:
        usage()
        sys.exit(0)
      if opt in ['-k', '--api_key']:
        self.api_key = arg
      elif opt in ['-p', '--pairs']:
        self.currency_pairs = arg.split(',')
        self.validate_currency_pairs()
      elif opt in ['-d', '--debug']:
        self.debug = True
      elif opt in ['-i', '--include-csv-headers']:
        self.include_csv_headers = True
      else:
        assert False, "Unhandled option"
    if not self.api_key:
      user_error('Missing argument api_key')
    if not self.currency_pairs:
      user_error('Missing argument pairs')
    # Remaining args only can be an output filename.  Take the first one
    # and ignore the rest.
    if positional_args:
      # We could enforce a extension 'csv' here, but I rather prefer
      # let users choose their names.
      self.output_file = positional_args[0]

  def validate_currency_pairs(self):
    currencies = ["EUR", "USD", "JPY", "GBP",
                  "CAD", "CHF", "AUD", "NZD",
                  "SGD", "NOK", "RUB", "SEK",
                  "TRY", "ZAR", "HKD", "CNH",
                  "DKK", "MXN", "PLN", "XAG",
                  "XAU", "BTC", "ETH", "LTC",
                  "XRP", "DSH", "BCH"]
    valid_pairs = [cur1 + cur2 for cur1 in currencies \
                   for cur2 in currencies \
                   if cur1 != cur2]
    for pair in self.currency_pairs:
      if pair not in valid_pairs:
        print("Detected invalid currency pair '%s'" %pair)
        exit(1)

  def do_http_request(self):
    uri = self.uri_end_point + "?pairs=" + ','.join(self.currency_pairs) + \
      "&api_key=" + self.api_key
    if self.debug:
      print "[DEBUG] HTTP GET request to uri: %s" %uri
    try:
      response = urllib2.urlopen(uri).read()
    except urllib2.URLError as e:
      print "Request failed", e
      sys.exit(1)
    if self.debug:
      print "[DEBUG] Received response from server: %s" %response
    json_data = json.loads(response)
    if 'error' in json_data and json_data['error']:
      print "Error response from server: %s" %json_data['message']
      sys.exit(1)
    return json_data

  def write_output(self, json_data):
    """
    Write server response into self.output_file in CSV format.

    A typical response is as follows:
    {"symbol":"EURJPY","bid":128.123,"ask":128.124,"price":128.1235,"timestamp":1540395225}
    """
    headers = ["symbol", "bid", "ask", "price", "timestamp"]
    with open(self.output_file, 'w') as file_:
      if self.include_csv_headers:
        file_.write(','.join(headers) + '\n')
      for entry in json_data:
        file_.write(','.join([str(entry[key]) for key in headers]) + '\n')

def user_error(error_msg=None):
  if error_msg:
    print error_msg
    usage()
    exit(1)

def print_output(json_data):
  for entry in json_data:
    print str(entry)

def usage():
  help_str = """Usage:
python currency_exchange.py api_key=API_KEY pairs=XXXYYY [--debug] [--include-csv-headers] [output.csv]

api_key: A valid API key to use the forex service
         (https://1forge.com/forex-data-api)
pairs: Comma separated currency pairs to translate, e.g. EURUSD,JPYUSD

Optional arguments:
--debug: Show debug information; default False.
--include-csv-headers: Include header in the CSV file; default False.
output.csv: A local filename where to write the output.
"""
  print help_str


if __name__ == '__main__':
  # if len(sys.argv) < 2:
    # user_error()
  cur_exchange = CurrencyExchange(*sys.argv[1:])
  json = cur_exchange.do_http_request()
  if cur_exchange.output_file:
    cur_exchange.write_output(json)
  else:
    print_output(json)
