from selenium import webdriver
import copy
import json
import os
import time
import urllib.request

#Global Variable Initialization
global failed_list

#Variable Initialization
path = './assets/'
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
email = 'vincent.budianto@gmail.com'
header = {'user-agent' : useragent, 'from': email}
filename_data_source = 'data/data_source.json'
filename_failed_link = 'data/image_failed_link.json'
failed_list = []

with open(os.path.join(path, filename_data_source), 'r', encoding='utf8') as json_file:
    operator_list = json.load(json_file)

#Image List
def image():
	global failed_list

	for operator in operator_list:
		if (operator['cn_link'].startswith('http://ak.mooncell.wiki/')):
			option = webdriver.ChromeOptions()
			option.add_argument('--incognito')
			browser = webdriver.Chrome(options=option)
			url = operator['cn_link']
			browser.get(url)
			count_skin_icon = 0
			count_skin = 0
			count_stage = 0

			skin_icon_element = browser.find_elements_by_xpath("//div[@class='charhead']//img")
			skin_element = browser.find_elements_by_xpath("//div[@class='charimg-skin']//img")
			stage_element = browser.find_elements_by_xpath("//div[@class='charimg-stage']//img")
			skin_icon_links = [icon.get_attribute('src') for icon in skin_icon_element if (icon.get_attribute('src') != '')]
			skin_links = [skin.get_attribute('src') for skin in skin_element if (skin.get_attribute('src') != '')]
			stage_links = [stage.get_attribute('src') for stage in stage_element if (stage.get_attribute('src') != '')]

			for skin_icon_link in skin_icon_links:
				count_skin_icon += 1
				filename = operator['en_name'] + '_skin_icon' + str(count_skin_icon) + '.png'
				print('Downloading', filename)

				try:
					urllib.request.urlretrieve(skin_icon_link, os.path.join((path + 'image/operators/' + operator['en_name'] + '/'), filename))
					print('Download finished')
				except Exception as e:
					print('Download failed |', str(e))
					failed_list.append([operator['en_name'], skin_icon_link, 'icon'])

			for skin_link in skin_links:
				count_skin += 1
				filename = operator['en_name'] + '_skin' + str(count_skin) + '.png'
				print('Downloading', filename)

				try:
					urllib.request.urlretrieve(skin_link, os.path.join((path + 'image/operators/' + operator['en_name'] + '/'), filename))
					print('Download finished')
				except Exception as e:
					print('Download failed |', str(e))
					failed_list.append([operator['en_name'], skin_link, 'skin'])

			for stage_link in stage_links:
				filename = operator['en_name'] + '_elite' + str(count_stage) + '.png'
				count_stage += 1
				print('Downloading', filename)

				try:
					urllib.request.urlretrieve(stage_link, os.path.join((path + 'image/operators/' + operator['en_name'] + '/'), filename))
					print('Download finished')
				except Exception as e:
					print('Download failed |', str(e))
					failed_list.append([operator['en_name'], stage_link, 'stage'])

			browser.quit()

	print('Failed: %d links' % len(failed_list))

	for i in range(len(failed_list)):
		print('%d. %s' % ((i + 1), failed_list[i]))

	failed_json()

def failed_json():
	global failed_list

	jdata = {}
	data = []

	for failed_data in failed_list:
		jdata['name'] = failed_data[0]
		jdata['link'] = failed_data[1]
		jdata['type'] = failed_data[2]
		data.append(copy.deepcopy(jdata))

	with open(os.path.join(path, filename_failed_link), 'w', encoding = 'utf8') as fileout:
		json.dump(data, fileout, ensure_ascii = False, indent = 4)

if (__name__ == '__main__'):
	image()