import sys, argparse
import socket
import dns.resolver
import time

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
      
      dns_list = []
      dns_list.append(args['@server'])

      my_resolver = dns.resolver.Resolver()
      my_resolver.nameservers = dns_list
      
      dns_start = time.perf_counter() # start time
      
      i = 0
      num_retries = args['r']
      for i in range(num_retries):
        answers = my_resolver.query(args['name'], request_type)
        if answers is not None:
            break
      
      dns_end = time.perf_counter() # end timer
      timer = (dns_end - dns_start) # get time to complete request

      print("Response received after {0} ({1} retries)\n".format(timer, i))
      print("***Answer Section ({0} records)***\n".format(len(answers)))

      if request_type is "A":
          label = 'IP'
      else:
          label = request_type

      if answers.canonical_name is not None:
          print("CNAME    {0}\t{1}\t{2}".format(answers.canonical_name, "[seconds can cache]", "[auth | nonauth]"))

      for answer in answers:
        print("{3}    {0}\t{1}\t{2}".format(answer.to_text(), "[seconds can cache]", "[auth | nonauth]", label))

      #print("------------------------------") 
      #print(answers.rrset)
      #print("------------------------------")

      print("***Additional Section ({0} records)".format(len(answers.response.additional)))
    
    #except:
    #  print('python DnsClient.py [-t timeout] [-r max-retries] [-p port] [-mx|-ns] @server name')
    #  sys.exit(2)
    


if __name__ == "__main__":
    main()