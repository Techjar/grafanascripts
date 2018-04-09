#!/usr/bin/python3
import requests, json, datetime, time
import config as cfg

while True:
	response = requests.get("http://" + cfg.xmrigproxy_address + "/workers.json")
	data = json.loads(response.text)

	query = ""
	for worker in data['workers']:
		query += worker[0] + " hashrate=" + str(worker[9] * 1000) + ",shares=" + str(worker[3]) + ",hashes=" + str(worker[6]) + "\n"

	response = requests.get("http://" + cfg.xmrigproxy_address)
	data = json.loads(response.text)
	query += cfg.xmrigproxy_total_name + " hashrate=" + str(data['hashrate']['total'][1] * 1000) + ",shares=" + str(data['results']['accepted']) + ",hashes=" + str(data['results']['hashes_total']) + "\n"

	requests.post(url = "http://localhost:8086/write?db=minerhash", data = query.encode('utf-8'), headers = {'Content-Type': 'application/octet-stream'})
	print(query)

	time.sleep(5)
