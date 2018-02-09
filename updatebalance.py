#!/usr/bin/python
import sys, requests

query = str(sys.argv[1]).lower() + " balance=" + str(sys.argv[2])

requests.post(url = "http://localhost:8086/write?db=cryptobalances", data = query.encode('utf-8'), headers = {'Content-Type': 'application/octet-stream'})
print 'Updated balance!'
