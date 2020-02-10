import sys, argparse
import socket

def main():
    #try:
      parser = argparse.ArgumentParser()
      parser.add_argument('-t', nargs='?', default=5)
      parser.add_argument('-r', nargs='?', default=3)
      parser.add_argument('-p', nargs='?', default=53)
      parser.add_argument('-mx', action='store_true')
      parser.add_argument('-ns',  action='store_true')
      parser.add_argument('@server')
      parser.add_argument('name')
      args = vars(parser.parse_args())

      if (args['mx'] == True) and (args['ns'] == True):
          print('-mx or -ns can be specified not both.')
          raise Exception()
      elif args['mx'] == True:
          request_type = 'MX'
      elif args['ns'] == True:
          request_type = 'NS'
      else:
          request_type = 'A'

      print("""
      DnsClient sending request for {0}\n
      Server: {1}\n
      Request type: {2}
      """.format(args['name'], args['@server'], request_type))

      #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      #s.connect(('www.mcgill.ca', 80))
      
      #s.close()
      

    #except:
    #  print('python DnsClient.py [-t timeout] [-r max-retries] [-p port] [-mx|-ns] @server name')
    #  sys.exit(2)
    


if __name__ == "__main__":
    main()