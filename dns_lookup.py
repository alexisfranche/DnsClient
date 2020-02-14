import socket
import ipaddress
import argparse
import time
import binascii

authority = 0

def parse_dns_string(reader, data):
    res = ''
    to_resue = None
    bytes_left = 0

    for ch in data:
        if not ch:
            break

        if to_resue is not None:
            resue_pos = chr(to_resue) + chr(ch)
            res += reader.reuse(resue_pos)
            break

        if bytes_left:
            res += chr(ch)
            bytes_left -= 1
            continue

        if (ch >> 6) == 0b11 and reader is not None:
            to_resue = ch - 0b11000000
        else:
            bytes_left = ch

        if res:
            res += '.'

    return res


class StreamReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read(self, len_):
        pos = self.pos
        if pos >= len(self.data):
            raise

        res = self.data[pos: pos+len_]
        self.pos += len_
        return res

    def reuse(self, pos):
        pos = int.from_bytes(pos.encode(), 'big')
        return parse_dns_string(None, self.data[pos:])


def make_dns_query_domain(domain):
    def f(s):
        return chr(len(s)) + s

    parts = domain.split('.')
    parts = list(map(f, parts))
    return ''.join(parts).encode()


def make_dns_request_data(dns_query, request_type):
    req = b'\xaa\xbb' #ID 
    req += b'\x01\x00' #LOTS OF STUFF (review)
    req += b'\x00\x01' #QDCOUNT should be 1 whatever that means
    req += b'\x00\x00' #ANCOUNT
    req += b'\x00\x00' #NSCOUNT can ignore whatever is in here
    req += b'\x00\x00' #ARCOUNT 
    req += dns_query #QNAME
    req += b'\x00' #signal termination of QNAME

    if request_type == 'A':
        req += b'\x00\x01' #QTYPE Modify depending on input  (A CHANGER)
    elif request_type == 'MX':
        req += b'\x00\x0f' # byte for MX
    else:
        req += b'\x00\x02' # bytes for NS

    req += b'\x00\x01' #QCLASS should be 00 01
    return req


def add_record_to_result(result, type_, data, reader):
    if type_ == 'A':
        item = str(ipaddress.IPv4Address(data))
    elif type_ == 'MX':
        item = parse_dns_string(reader, data)
    elif type_ == 'NS':
        item = parse_dns_string(reader, data)
    elif type_ == 'CNAME':
        item = parse_dns_string(reader, data)
    else:
        return

    result.setdefault(type_, []).append(item)


def parse_dns_response(res, dq_len, req): #dq_len is length of our request query
    reader = StreamReader(res)
    x = len(reader.data)
    def get_query(s):
        return s[12:12+dq_len]

    data = reader.read(len(req))
    
    assert(get_query(data) == get_query(req))#check same beginning

    def to_int(bytes_):
        return int.from_bytes(bytes_, 'big')

    result = {}
    res_num = to_int(data[6:8])     #number of records
    tmp = bin(to_int(data[2:4]))
    AA = tmp[7]
    if(AA == 0):
        authority = "nonauth"
    else:
        authority = "auth"
    result.update({'AA': AA})
    authCount = to_int(data[8:10])
    addCount = to_int(data[10:12])
    print("num auth ans ", authCount)
    print("num add ans ", addCount)





    #get TLL
    # start = 12 + dq_len + 1 + 4 + 2 + 4 #starts at 0 
    # print("TTL ", res[start:start+4])
    # TLL = to_int(res[start : start + 4])
    # result.update({'TTL': TLL})
    #get TLLs

    print("***Answer Section ({0} records)***".format(res_num))

    for i in range(res_num):
        #Answer
        a = reader.read(2)#NAME
        
        type_num = to_int(reader.read(2)) #TYPE
        

        type_ = None
        if type_num == 1:
            type_ = 'A'
        elif type_num == 2:
            type_ = 'NS'
        elif type_num == 5:
            type_ = 'CNAME'
        elif type_num == 15:
            type_ = 'MX'

        b = reader.read(2) #CLASS 
        TTL = reader.read(4)
        print("TTL ", TTL)
        TTL = to_int(TTL)
        datalen = to_int(reader.read(2)) #RDLENGTH

        if type_ == 'MX':
            pref = to_int(reader.read(2))#PREF
            data = reader.read(datalen-2)#EXCHANGE
        else:        
            data = reader.read(datalen)#RDATA
    
        #add_record_to_result(result, type_, data, reader)

        if type_ == 'A':
            item = str(ipaddress.IPv4Address(data))
            print("IP   {0}   {1}   {2}".format(item,TTL,authority))
        elif type_ == 'MX':
            item = parse_dns_string(reader, data)
            print("MX   {0}   {1}   {2}   {3}".format(item, pref, TTL, authority))
        elif type_ == 'NS':
            item = parse_dns_string(reader, data)
            print("NS   {0}   {1}   {2}".format(item, TTL, authority))
        elif type_ == 'CNAME':
            item = parse_dns_string(reader, data)
            print("CNAME    {0}   {1}   {2}".format(item,TTL, authority))
        

        result.setdefault(type_, []).append(item)

    for i in range(authCount):
        reader.read(2)
        reader.read(2)
        reader.read(6)
        temp = reader.read(2)
        temp = reader.read(to_int(temp))

    print("***Additional Section ({0} records)***".format(addCount))

    if addCount == 0:
        print("NOTFOUND")
    else:
        for j in range(addCount):
                #Answer
            a = reader.read(2)#NAME
            
            type_num = to_int(reader.read(2)) #TYPE

            

            type_ = None
            if type_num == 1:
                type_ = 'A'
            elif type_num == 2:
                type_ = 'NS'
            elif type_num == 5:
                type_ = 'CNAME'
            elif type_num == 15:
                type_ = 'MX'

            b = reader.read(2) #CLASS 
            TTL = reader.read(4)
            print("TTL ", TTL)
            TTL = to_int(TTL)
            datalen = to_int(reader.read(2)) #RDLENGTH

            if type_ == 'MX':
                pref = to_int(reader.read(2))#PREF
                data = reader.read(datalen-2)#EXCHANGE
            else:        
                data = reader.read(datalen)#RDATA
        
            #add_record_to_result(result, type_, data, reader)

            if type_ == 'A':
                item = str(ipaddress.IPv4Address(data))
                print("IP   {0}   {1}   {2}".format(item,TTL,authority))
            elif type_ == 'MX':
                item = parse_dns_string(reader, data)
                print("MX   {0}   {1}   {2}   {3}".format(item, pref, TTL, authority))
            elif type_ == 'NS':
                item = parse_dns_string(reader, data)
                print("NS   {0}   {1}   {2}".format(item, TTL, authority))
            elif type_ == 'CNAME':
                item = parse_dns_string(reader, data)
                print("CNAME    {0}   {1}   {2}".format(item,TTL, authority))

            result.setdefault(type_, []).append(item)
    


    return result



def dns_lookup(domain, address, port, num_retries, request_type, timeout):
    dns_query = make_dns_query_domain(domain)
    dq_len = len(dns_query)

    req = make_dns_request_data(dns_query, request_type)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.settimeout(timeout)

    dns_start = time.perf_counter() # start time
    
    i = 0
    for i in range(num_retries):
        sock.sendto(req, (address, port))
        res, _ = sock.recvfrom(1024 * 4)
        if res is not None:
            break

    if i == num_retries:
        raise Exception("ERROR Maximum number of retries {0} exceeded".format(num_retries))
    
    dns_end = time.perf_counter() # end time
    timer = (dns_end - dns_start)
    print("Response received after {0} ({1} retries)\n".format(timer, i))
    print("res from socket ", res)
    result = parse_dns_response(res, dq_len, req)

    sock.close()

    return result

def main():
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
        raise Exception('-mx or -ns can be specified not both.')
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

    print(dns_lookup(args['name'], args['@server'], int(args['p']), int(args['r']), request_type, int(args['t'])))

if __name__ == '__main__':
    main()
