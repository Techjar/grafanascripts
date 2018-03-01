#!/usr/bin/python3
import requests, json, datetime, time, traceback
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost', port=8086)

def update_value(name, lite):
	miner_db = 'minerhash_lite' if lite else 'minerhash'
	client.switch_database('cryptovalues')
	price = list(client.query('select price from ' + name + ' order by desc limit 1').get_points())[0]['price']
	client.switch_database('coinprofit')
	sat_per_hash = list(client.query('select sat_per_hash from ' + name + ' order by desc limit 1').get_points())[0]['sat_per_hash']
	client.switch_database(miner_db)
	for miner in client.get_list_measurements():
		client.switch_database(miner_db)
		try:
			hashrate = list(client.query('select hashrate from ' + miner['name'] + ' order by desc limit 1').get_points())[0]['hashrate']
			client.switch_database('profitestimates')
			sat_per_day = sat_per_hash * hashrate * 86400
			fiat_per_day = sat_per_day * price
			print(miner['name'] + '_' + name, sat_per_day, fiat_per_day)
			client.write_points([{'measurement': miner['name'] + '_' + name, 'fields': {'sat_per_hash': sat_per_hash, 'sat_per_day': sat_per_day, 'fiat_per_day': fiat_per_day}}])
		except KeyboardInterrupt:
			raise
		except:
			print('Error updating', miner['name'] + '_' + name)
			traceback.print_exc()

while True:
	update_value('xmr', False)
	update_value('etn', False)
	update_value('aeon', True)
	update_value('itns', False)
	update_value('msr', False)
	update_value('trtl', False)
	update_value('krb', False)
	update_value('dero', False)
	update_value('xao', False)
	update_value('bbs', False)

	time.sleep(5)

