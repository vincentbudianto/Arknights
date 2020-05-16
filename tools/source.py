from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import bs4
import copy
import json
import os
import requests
import time

#Global Variable Initialization
global cn_data
global en_data
global failed_list
global operator_list

#Variable Initialization
path = './assets/'
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
email = 'vincent.budianto@gmail.com'
header = {'user-agent' : useragent, 'from': email}
filename_data_source = 'data/data_source.json'
filename_failed_link = 'data/data_failed_link.json'
cn_data = []
en_data = []
failed_list = []
operator_list = []

with open(os.path.join(path, filename_data_source), 'r', encoding='utf8') as json_file:
    operator_list_json = json.load(json_file)

for data in operator_list_json:
	operator_list.append([data['en_name'], data['cn_name'], data['jp_name'], data['code'], data['class'], data['faction'], data['rarity'], data['acquisition'], data['en_link'], data['cn_link']])

#Operator List
def operator():
	global cn_data

	option = webdriver.ChromeOptions()
	option.add_argument('--incognito')
	browser = webdriver.Chrome(options=option)
	url = 'http://ak.mooncell.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88'
	browser.get(url)
	timeout = 20

	try:
		Select(browser.find_element_by_id('per-page')).select_by_visible_text('500')
		WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//table[@class='wikitable']")))
	except TimeoutException:
		print('Timed out waiting for page to load')
		browser.quit()

	soup = bs4.BeautifulSoup(browser.page_source, 'html.parser')

	table = soup.find(id = 'result-table')
	rows = table.find_all('tr', {'class': 'result-row'})

	for row in rows:
		data = row.find('td').next_sibling

		names = data.find_all('div')
		names.pop(0)

		_cn_name = names[0].text
		_en_name = names[1].text

		if (names[2].text == ''):
			_jp_name = names[1].text
		else:
			_jp_name = names[2].text

		_code = names[3].text
		_cn_link = 'http://ak.mooncell.wiki' + data.find('a', href = True)['href']

		cn_data.append([_en_name, _cn_name, _jp_name, _code, _cn_link])

	print('%3d chinese links listed' % len(cn_data))

	browser.quit()

	operator_links()

def operator_links():
	global en_data

	url = 'https://mrfz.fandom.com/wiki/Operator_List'
	request = requests.get(url, headers = header, timeout = 20)
	soup = bs4.BeautifulSoup(request.text, 'html.parser')

	table = soup.find('table', {'class': 'mrfz-wtable'})
	rows = table.find_all('tr')
	rows.pop(0)

	for row in rows:
		cols = row.find_all('td')
		cols.pop(0)

		_name = cols[0].text.replace('\n', '')
		_class = cols[1].text.replace('\n', '')
		_faction = cols[2].find('a')['title']
		_rarity = cols[3].text.replace('\n', '')
		_en_link = 'https://mrfz.fandom.com' + cols[0].find('a', href = True)['href']

		en_data.append([_name, _class, _faction, _rarity, _en_link])

	print('%3d english links listed' % len(en_data))

	operator_details()

def operator_details():
	global cn_data
	global en_data
	global failed_list
	global operator_list

	added_operator = []
	updated_operator = []

	if (len(cn_data) == len(en_data)):
		for data in en_data:
			try:
				print('Collecting %s data...' % data[0])
				_url = data[4]
				request = requests.get(_url, headers = header, timeout = 20)
				soup = bs4.BeautifulSoup(request.text, 'html.parser')

				table = soup.find('div', {'class': 'op-info'})
				rows = table.find_all('tr')
				rows.pop(0)
				rows.pop(0)
				cols = rows[1].find_all('td')

				_acquisition = cols[1].text.replace('\n', '').split(', ')
				_cn_name = cols[2].find('big').text

				for i, data_cn in enumerate(cn_data):
					for j, cn_name in enumerate(data_cn):
						if (cn_name == _cn_name):
							if (cn_data[i][0] != data[0]):
								cn_data[i][0] = data[0]

							operator = [cn_data[i][0], cn_data[i][1], cn_data[i][2], cn_data[i][3], data[1], data[2], data[3], _acquisition, _url, cn_data[i][4]]

							if (operator not in operator_list):
								updated = False
								directory = os.path.join(path, ('image/operators/' + data[0]))

								for k, old_data in enumerate(operator_list):
									if (operator[0] == old_data[0]):
										updated = True

										updated_operator.append([old_data, operator])
										operator_list.pop(k)

								operator_list.append(operator)

								if (not updated):
									added_operator.append(operator)

								if (not os.path.exists(directory)):
									os.mkdir(directory)
			except Exception as e:
				print('Collecting %s data failed | %s' % (data[0], str(e)))
				failed_list.append([data[0], data[4]])

			time.sleep(2)

		operator_list.sort()

		print('\n%d operators listed' % len(operator_list))
		print('\nAdded %d new operators' % len(added_operator))

		for l in range(len(added_operator)):
			print('%3d. %s' % ((l + 1), added_operator[l][0]))

		print('\nUpdated %d operators' % len(updated_operator))

		for m in range(len(updated_operator)):
			print('%3d. %s' % ((m + 1), updated_operator[m][0][0]))

			for n in range(len(updated_operator[m][0])):
				if (updated_operator[m][0][n] != updated_operator[m][1][n]):
					print('%s  -->  %s' % (updated_operator[m][0][n], updated_operator[m][1][n]))

		print('\nFailed: %d links' % len(failed_list))

		for o in range(len(failed_list)):
			print('%3d. %s' % ((o + 1), failed_list[o]))

		if (len(failed_list) > 0):
			failed_data_json()

		data_source_json()
	else:
		print('Invalid data count | (cn) %3d : %3d (en)' % (len(cn_data), len(en_data)))

def failed_data_json():
	global failed_list

	jdata = {}
	data = []

	for failed_data in failed_list:
		jdata['name'] = failed_data[0]
		jdata['link'] = failed_data[1]
		data.append(copy.deepcopy(jdata))

	with open(os.path.join(path, filename_failed_link), 'w', encoding = 'utf8') as fileout:
		json.dump(data, fileout, ensure_ascii = False, indent = 4)

def data_source_json():
	global operator_list

	jdata = {}
	data = []

	for operator in operator_list:
		jdata['en_name'] = operator[0]
		jdata['cn_name'] = operator[1]
		jdata['jp_name'] = operator[2]
		jdata['code'] = operator[3]
		jdata['class'] = operator[4]
		jdata['faction'] = operator[5]
		jdata['rarity'] = operator[6]
		jdata['acquisition'] = operator[7]
		jdata['en_link'] = operator[8]
		jdata['cn_link'] = operator[9]
		data.append(copy.deepcopy(jdata))

	with open(os.path.join(path, filename_data_source), 'w', encoding = 'utf8') as fileout:
		json.dump(data, fileout, ensure_ascii = False, indent = 4)

if (__name__ == '__main__'):
	operator()
