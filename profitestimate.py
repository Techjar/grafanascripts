#!/usr/bin/python3
import requests, json, datetime, time
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost', port=8086)

def update_value(name, lite):
	client.switch_database('cryptovalues')
	values = list(client.query('select * from ' + name + ' order by desc limit 1').get_points())[0]
	client.switch_database('coinprofit')
	sat_per_hash = list(client.query('select * from ' + name + ' order by desc limit 1').get_points())[0]['sat_per_hash']
	if lite:
		client.switch_database('minerhash_lite')
	else:
		client.switch_database('minerhash')
	for miner in client.get_list_measurements():
		if lite:
			client.switch_database('minerhash_lite')
		else:
			client.switch_database('minerhash')
		while True:
			hash = list(client.query('select * from ' + miner['name'] + ' order by desc limit 1').get_points())[0]
			# Work around unidentifed InfluxDB issue
			if hash is None:
				continue
			client.switch_database('profitestimates')
			sat_per_day = sat_per_hash * hash['hashrate'] * 86400
			fiat_per_day = sat_per_day * values['price']
			print(miner['name'] + '_' + name, sat_per_day, fiat_per_day)
			client.write_points([{'measurement': miner['name'] + '_' + name, 'fields': {'sat_per_hash': sat_per_hash, 'sat_per_day': sat_per_day, 'fiat_per_day': fiat_per_day}}])
			break

while True:
	update_value('xmr', False)
	update_value('etn', False)
	update_value('aeon', True)
	update_value('itns', False)
	update_value('msr', False)
	update_value('trtl', False)
	update_value('krb', False)
	update_value('dero', False)

	time.sleep(5)

