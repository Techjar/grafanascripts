#!/usr/bin/python3
import requests, json, datetime, time, traceback
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost', port=8086)
fiat_currency = "USD"
times = {}

def get_info_cmc(id):
	response = requests.get("https://api.coinmarketcap.com/v1/ticker/" + id + "/?convert=" + fiat_currency)
	data = json.loads(response.text)[0]
	market_cap = data['market_cap_' + fiat_currency.lower()]
	return {'price': float(data['price_' + fiat_currency.lower()]), 'market_cap': float(market_cap if market_cap is not None else 0)}

def get_info_southxchange(id):
	response = requests.get("http://www.southxchange.com/api/prices")
	data = json.loads(response.text)
	for market in data:
		if market['Market'] == id + '/BTC':
			return {'price': float(market['Last']) * get_info_cmc('bitcoin')['price'], 'market_cap': 0.0}
	return {'price': 0.0, 'market_cap': 0.0}

def get_info_tradeogre(id):
	response = requests.get("https://tradeogre.com/api/v1/ticker/BTC-" + id)
	data = json.loads(response.text)
	return {'price': float(data['price']) * get_info_cmc('bitcoin')['price'], 'market_cap': 0.0}

def update_value(name, price_id, info_function, interval):
	try:
		if name in times and time.perf_counter() - times[name] < interval:
			return
		times[name] = time.perf_counter()

		client.switch_database('cryptobalances')
		result = list(client.query('select * from ' + name + ' order by desc limit 1').get_points())
		balance = float(0)
		if len(result) > 0:
			balance = float(result[0]['balance'])
		client.switch_database('cryptovalues')

		info = info_function(price_id)
		value = balance * info['price']

		client.write_points([{'measurement': name, 'fields': {'price': info['price'], 'balance': balance, 'value': value, 'market_cap': info['market_cap']}}])
		print(name, info['price'], balance, value, info['market_cap'])
	except KeyboardInterrupt:
		raise
	except:
		print('Error updating', name)
		traceback.print_exc()

while True:
	update_value('xmr', 'monero', get_info_cmc, 150)
	update_value('etn', 'electroneum', get_info_cmc, 150)
	update_value('eth', 'ethereum', get_info_cmc, 150)
	update_value('etc', 'ethereum-classic', get_info_cmc, 150)
	update_value('bch', 'bitcoin-cash', get_info_cmc, 150)
	update_value('aeon', 'aeon', get_info_cmc, 150)
	update_value('zcl', 'zclassic', get_info_cmc, 150)
	update_value('itns', 'intensecoin', get_info_cmc, 150)
	update_value('msr', 'MSR', get_info_southxchange, 30)
	update_value('btc', 'bitcoin', get_info_cmc, 150)
	update_value('ltc', 'litecoin', get_info_cmc, 150)
	update_value('trtl', 'TRTL', get_info_tradeogre, 30)
	update_value('jnt', 'jibrel-network', get_info_cmc, 150)

	time.sleep(1)
