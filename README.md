# DnsClient

Python version 3.7
Works on Mac and Windows

Get started:

python DnsClient.py [-t timeout] [-r max-retries] [-p port] [-mx|-ns] @server name

wheretheargumentsaredefinedasfollows.
• timeout(optional) gives how long to wait, in seconds, before retransmitting an
unanswered query. Default value: 5.
• max-retries(optional)isthemaximumnumberoftimestoretransmitanunanswered
query before giving up. Default value: 3.
• port(optional)is the UDP port number of the DNS server. Default value: 53.
• -mx or -ns flags (optional) indicate whether to send a MX (mail server) or NS (name server)
query. At most one ofthese can be given, and if neither is given then the client should send a
type A (IP address) query.
• server (required) is the IPv4 address of the DNS server, in a.b.c.d.format
• name (required) is the domain name to query for.
