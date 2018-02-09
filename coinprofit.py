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
	response = requests.get("https://whattomine.com/coins/192.json")
	data = json.loads(response.text)
	sats = (1 / data['difficulty']) * data['block_reward']
	update_profit('aeon', sats, float(data['nethash']), float(data['difficulty']), float(data['block_reward']))

def update_profit_itns():
	response = requests.get("https://pool.intensecoin.net/api/stats", verify=False)
	data = json.loads(response.text)
	sats = (1 / float(data['network']['difficulty'])) * (float(data['network']['reward']) / float(data['config']['denominationUnit']))
	update_profit('itns', sats, float(data['network']['difficulty']) / float(data['config']['coinDifficultyTarget']), float(data['network']['difficulty']), float(data['network']['reward']))

def update_profit_msr():  
	response = requests.get("https://masari.superpools.net/api/stats")
	data = json.loads(response.text)
	sats = (1 / float(data['network']['difficulty'])) * (float(data['network']['reward']) / float(data['config']['coinUnits']))
	update_profit('msr', sats, float(data['network']['difficulty']) / float(data['config']['coinDifficultyTarget']), float(data['network']['difficulty']), float(data['network']['reward']))

def update_profit_trtl():
	response = requests.get("https://trtl.mine2gether.com/api/stats")
	data = json.loads(response.text)
	sats = (1 / float(data['network']['difficulty'])) * (float(data['network']['reward']) / float(data['config']['coinUnits']))
	update_profit('trtl', sats, float(data['network']['difficulty']) / float(data['config']['coinDifficultyTarget']), float(data['network']['difficulty']), float(data['network']['reward']))

def update_profit_dero():
	response = requests.get("https://dero.miner.rocks/api/stats")
	data = json.loads(response.text)
	sats = (1 / float(data['network']['difficulty'])) * (float(data['network']['reward']) / float(data['config']['coinUnits']))
	update_profit('dero', sats, float(data['network']['difficulty']) / float(data['config']['coinDifficultyTarget']), float(data['network']['difficulty']), float(data['network']['reward']))

def update_profit_krb():
	response = requests.get("https://krb.miner.rocks/api/stats")
	data = json.loads(response.text)
	sats = (1 / float(data['network']['difficulty'])) * (float(data['network']['reward']) / float(data['config']['coinUnits']))
	update_profit('krb', sats, float(data['network']['difficulty']) / float(data['config']['coinDifficultyTarget']), float(data['network']['difficulty']), float(data['network']['reward']))

def update_whattomine():
	global whattomine_data
	response = requests.get("https://whattomine.com/coins.json")
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
	robust_call(update_profit_itns)
	robust_call(update_profit_msr)
	robust_call(update_profit_trtl)
	robust_call(update_profit_dero)
	robust_call(update_profit_krb)

	time.sleep(60)
