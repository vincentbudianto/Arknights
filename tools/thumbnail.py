from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import copy
import json
import os
import urllib.request

#Global Variable Initialization
global cn_names
global failed_list

#Variable Initialization
path = './assets/'
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
email = 'vincent.budianto@gmail.com'
header = {'user-agent' : useragent, 'from': email}
filename_data_source = 'data/data_source.json'
filename_failed_link = 'data/thumbnail_failed_link.json'
cn_names = []
failed_list = []

with open(os.path.join(path, filename_data_source), 'r', encoding='utf8') as json_file:
    operator_list = json.load(json_file)

for data in operator_list:
	cn_names.append(data['cn_name'])

#Thumbnail List
def thumbnail():
	global cn_names
	global failed_list

	option = webdriver.ChromeOptions()
	option.add_argument('--incognito')
	browser = webdriver.Chrome(options=option)
	url = 'http://ak.mooncell.wiki/w/%E5%B9%B2%E5%91%98%E4%B8%80%E8%A7%88'
	browser.get(url)
	timeout = 20

	try:
		WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//table")))
		Select(browser.find_element_by_id('per-page')).select_by_visible_text('500')
		WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//img")))
		browser.find_element_by_xpath("//div[@id='min-cb']//div//label//span").click()
		WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.XPATH, "//img")))
		images_element = browser.find_elements_by_xpath("//div[@class='svt']//img")
		names_element = browser.find_elements_by_xpath("//div[@class='cn']")
		thumbnail_links = [('http:' + image.get_attribute('data-src').replace('110px', '150px')) for image in images_element]
		names = [name.text for name in names_element]
	except TimeoutException:
		print('Timed out waiting for page to load')
		browser.quit()

	if (len(thumbnail_links) == len(names)):
		for i in range(len(thumbnail_links)):
			for j, name in enumerate(cn_names):
				if (names[i] == name):
					filename = operator_list[j]['en_name'] + '_thumbnail.png'
					print('Downloading', filename)

					try:
						urllib.request.urlretrieve(thumbnail_links[i], os.path.join((path + 'image/operators/' + operator_list[j]['en_name'] + '/'), filename))
						print('Download finished')
					except Exception as e:
						print('Download failed |', str(e))
						failed_list.append([operator_list[j]['en_name'], thumbnail_links[i]])

		print('Failed: %d links' % len(failed_list))

		for l in range(len(failed_list)):
			print('%3d. %s' % ((l + 1), failed_list[l]))

		failed_thumbnail_json()
	else:
		print('Length failure')

def failed_thumbnail_json():
	global failed_list

	jdata = {}
	data = []

	for thumbnail in failed_list:
		jdata['name'] = thumbnail[0]
		jdata['link'] = thumbnail[1]
		data.append(copy.deepcopy(jdata))

	with open(os.path.join(path, filename_failed_link), 'w', encoding = 'utf8') as fileout:
		json.dump(data, fileout, ensure_ascii = False, indent = 4)

if (__name__ == '__main__'):
	thumbnail()