#!/usr/bin/python3
import requests, json, datetime, time, traceback, urllib3
from influxdb import InfluxDBClient

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

client = InfluxDBClient(host='localhost', port=8086)

whattomine_data = {}

def update_profit(name, sat_per_hash, nethash, difficulty, block_reward):
	client.switch_database('coinprofit')
	client.write_points([{'measurement': name, 'fields': {'sat_per_hash': sat_per_hash, 'nethash': nethash, 'difficulty': difficulty, 'block_reward': block_reward}}])
	print(name, sat_per_hash, nethash, difficulty, block_reward)

def update_profit_cryptonight(name, id):
	sats = (1 / whattomine_data[id]['difficulty']) * whattomine_data[id]['block_reward']
	update_profit(name, sats, float(whattomine_data[id]['nethash']), float(whattomine_data[id]['difficulty']), float(whattomine_data[id]['block_reward']))

def update_profit_aeon():
	response = requests.get("https://whattomine.com/coins/192.json", timeout=5)
	data = json.loads(response.text)
	sats = (1 / data['difficulty']) * data['block_reward']
	update_profit('aeon', sats, float(data['nethash']), float(data['difficulty']), float(data['block_reward']))

def update_profit_cnupool(name, pool_addr, url="/api/stats", https=True, https_verify=True):
	response = requests.get(("https" if https else "http") + "://" + pool_addr + url, timeout=5, verify=https_verify)
	data = json.loads(response.text)
	sats = (1 / float(data['network']['difficulty'])) * (float(data['network']['reward']) / float(data['config']['coinUnits']))
	update_profit(name, sats, float(data['network']['difficulty']) / float(data['config']['coinDifficultyTarget']), float(data['network']['difficulty']), float(data['network']['reward']) / float(data['config']['coinUnits']))

def update_whattomine():
	global whattomine_data
	response = requests.get("https://whattomine.com/coins.json", timeout=5)
	whattomine_data = json.loads(response.text)['coins']

def robust_call(func):
	try:
		func()
	except KeyboardInterrupt:
		raise
	except:
		print('Error updating')
		traceback.print_exc()

while True:
	robust_call(update_whattomine)
	robust_call(lambda: update_profit_cryptonight('xmr', 'Monero'))
	robust_call(lambda: update_profit_cryptonight('etn', 'Electroneum'))
	robust_call(update_profit_aeon)
	robust_call(lambda: update_profit_cnupool('itns', 'pool.intensecoin.net', https_verify=False))
	robust_call(lambda: update_profit_cnupool('msr', 'masari.superpools.net'))
	robust_call(lambda: update_profit_cnupool('trtl', 'trtl.mine2gether.com'))
	robust_call(lambda: update_profit_cnupool('dero', 'dero.miner.rocks'))
	robust_call(lambda: update_profit_cnupool('krb', 'krb.miner.rocks'))
	robust_call(lambda: update_profit_cnupool('xao', 'alloypool.com'))
	robust_call(lambda: update_profit_cnupool('bbs', 'bbs.pool.pilbeams.net:8111', url='/stats', https=False))

	time.sleep(60)
