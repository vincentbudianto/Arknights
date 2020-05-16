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
import urllib.request

#Global Variable Initialization
global cn_links
global failed_list
global icon_list

#Variable Initialization
path = './assets/'
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
email = 'vincent.budianto@gmail.com'
header = {'user-agent' : useragent, 'from': email}
filename_data_source = 'data/data_source.json'
filename_failed_link = 'data/icon_failed_link.json'
cn_links = []
failed_list = []
icon_list = []

with open(os.path.join(path, filename_data_source), 'r', encoding='utf8') as json_file:
    operator_list = json.load(json_file)

for data in operator_list:
	cn_links.append(data['cn_link'])

#Icon List
def icon():
	global cn_links
	global failed_list
	global icon_list

	option = webdriver.ChromeOptions()
	option.add_argument('--incognito')
	browser = webdriver.Chrome(options=option)
	url = 'http://ak.mooncell.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88'
	browser.get(url)
	timeout = 20

	try:
		Select(browser.find_element_by_id('per-page')).select_by_visible_text('500')
		WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//img")))
	except TimeoutException:
		print('Timed out waiting for page to load')
		browser.quit()

	soup = bs4.BeautifulSoup(browser.page_source, 'html.parser')

	table = soup.find(id = 'result-table')
	operators = table.find_all('a', href = True)

	for i in operators:
		if (i.text == ''):
			operator_icon = 'http:' + i.find('img')['data-src']
			link = 'http://ak.mooncell.wiki' + str(i['href'])
			icon_list.append([operator_icon, link])

	for icon in icon_list:
		for j, cn_link in enumerate(cn_links):
			if (icon[1] == cn_link):
				filename = operator_list[j]['en_name'] + '_icon.png'
				print('Downloading', filename)

				try:
					urllib.request.urlretrieve(icon[0], os.path.join((path + 'image/operators/' + operator_list[j]['en_name'] + '/'), filename))
				except Exception as e:
					print('Download failed |', str(e))
					failed_list.append([operator_list[j]['en_name'], icon[0]])

	print('Failed: %d links' % len(failed_list))

	for l in range(len(failed_list)):
		print('%3d. %s' % ((l + 1), failed_list[l]))

	failed_icon_json()

def failed_icon_json():
	global failed_list

	jdata = {}
	data = []

	for icon in failed_list:
		jdata['name'] = icon[0]
		jdata['link'] = icon[1]
		data.append(copy.deepcopy(jdata))

	with open(os.path.join(path, filename_failed_link), 'w', encoding = 'utf8') as fileout:
		json.dump(data, fileout, ensure_ascii = False, indent = 4)

if (__name__ == '__main__'):
	icon()
