import time
import traceback
import re, random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# binary = input('Full path to Chromium binary: ')

tw = input('Enter Twonky address in <ip:port> format: ')

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-logging')
options.add_argument('--ignore-certificate-errors')
# options.binary_location = binary

try:
	driver = webdriver.Chrome(options=options)
	driver.set_page_load_timeout(75)
	driver.get(f'http://{tw}/webbrowse#photo')
	time.sleep(2)
except:
	traceback.print_exc()
	print("\nError..Retry?")
	driver.quit()
	exit(0)


alt_version = False
albums = []
links = []
a_num = 0
r_n = 0
d = {}


def get_pages(p):
	try:
		pages = driver.find_elements_by_xpath(f'//*[@id=\
"browsePages"]/div[1]/a[{p}]')[0]
		pages.click()
		time.sleep(1)
	except:
		pass


def get_albums():
	global alt_version, albums, a_num, r_n, d

	if r_n == 0:
		try:
			title = driver.find_elements_by_id('title')
			a_sum = len(title)
		except:
			traceback.print_exc()
			print('\nError processing server. Retry or give up :c')
			driver.quit()
			exit(0)

		a_tag = 0
		for tit in title:
			if a_tag > 10:
				break
			try:
				al_num = tit.find_elements_by_class_name('smallFont')
				a_name = tit.find_elements_by_class_name('truncate')
				a_re = al_num[0].get_attribute('innerHTML')
				a_total = int(re.search(r'\d+', a_re).group())
				d.setdefault(a_name[0].get_attribute('innerHTML'), a_total)
			except IndexError:
				alt_version = True
				a_total = '??'
				a_name = tit.find_elements_by_xpath('//*[@id="title"]/a')
				try:
					d.setdefault(a_name[a_tag].get_attribute('innerHTML'), a_total)
					a_tag += 1
				except:
					print('The code does not support this \
version of Twonky firmware, sorry :c')
					driver.quit()
					exit(0)

	p = 1
	while True:
		try:
			title = driver.find_elements_by_id('title')
			a_sum = len(title)
		except:
			break

		if a_sum < 1:
			print(f'Not a recursive album..skip \
[recursion: {r_n} / 10]', end='\r')
			break

		for a in range(a_sum):
			if a % 6 == 0:
				html = driver.find_element_by_tag_name('html')
				for f in range(3):
					html.send_keys(Keys.PAGE_DOWN)
				time.sleep(1)

			print(f'Trying to add album in scope: {a} / {a_sum}. \
Total: {a_num}.    [page: {p} | recursion: {r_n} / 10]', end='\r')

			try:
				find = driver.find_elements_by_class_name('byFolderContainer')
				if alt_version:
					f_inner = find[a].get_attribute('innerHTML')
				else:
					f_inner = find[a].get_attribute('onclick')
				src = f_inner.split("'")[1]
				albm = f'http://{tw}/webbrowse#{src}'
				if albm not in albums:
					albums.append(albm)
					a_num += 1
			except:
				#traceback.print_exc()
				continue

		try:
			find_p = driver.find_elements_by_xpath('//*[@id=\
"browsePages"]/div[2]')[0]
			find_t = find_p.get_attribute('innerHTML')
			total_p = find_t.split(" ")[2]
		except:
			#traceback.print_exc()
			break

		if total_p and p < int(total_p) > 1:
			get_pages(p)
			p += 1
		else:
			break

def recursion():
	for album in albums:
		try:
			driver.get(album)
			get_albums()
		except:
			continue

def get_links(album, counter, succ=True):
	global alt_version, albums, links

	print(f'\n\nTrying to scrap pics from album\
 {counter} / {len(albums)}..')
	try:
		driver.get(album)
		time.sleep(2)
	except:
		#traceback.print_exc()
		print('Network error..skipping this one')
		succ = False

	p = 1
	while succ:
		try:
			photos = driver.find_elements_by_class_name('allPhotosItem')
		except:
			traceback.print_exc()
			print('No pictures found, trying another album..')
			break

		if len(photos) < 1:
			print('Oops..no pics here..')
			break

		d_div = 0
		for pic in photos:
#			if d_div % 5 == 0:
#				time.sleep(1)
			if d_div == 10 or d_div % 100 == 0:
				html = driver.find_element_by_tag_name('html')
				for f in range(60):
					if d_div == 10:
						html.send_keys(Keys.PAGE_DOWN)
					else:
						html.send_keys(Keys.PAGE_UP)
						if f > 20:
							break
				time.sleep(5)

			if alt_version:
				try:
					url = pic.find_elements_by_xpath(f'//*[@id=\
"item{d_div}"]/div/div[1]/a')
					r_url = url[0].get_attribute('onclick')
					i_url = re.findall(r'(?:http\:|https\:)?\/\/127.0.0.1.*', r_url)
					b_ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', i_url[0])
				except:
					#traceback.print_exc()
					d_div += 1
					continue
				p_link = i_url[0].replace(b_ip[0], tw.split(':')[0])
				d_url = p_link.split("'")[0]

			else:
				try:
					url = pic.find_elements_by_xpath(f'//*[@id="browseContents"]/\
div[3]/div/div[{d_div+1}]/div[1]/a')
					r_url = url[0].get_attribute('href')
					b_ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', r_url)
				except:
					#traceback.print_exc()
					if len(albums) == 1 and d_div == 1:
						alt_version = True
					d_div += 1
					continue
				d_url = r_url.replace(b_ip[0], tw.split(':')[0])

			if d_url and d_url not in links:
				links.append(d_url)
			d_div += 1
			print(f'Scraping links..Total: {d_div} \
/ {len(photos)}. Page: {p}', end ='\r')

		try:
			find_p = driver.find_elements_by_xpath('//*[@id=\
"browsePages"]/div[2]')[0]
			find_t = find_p.get_attribute('innerHTML')
			total_p = find_t.split(" ")[2]
		except:
			#traceback.print_exc()
			break

		if total_p and p < int(total_p) > 1:
			get_pages(p)
			p += 1
		else:
			break


def html():
	global links

	url = 0
	print('\n\n')

	with open('%s.html' % (tw.split(':')[0]), 'w') as html:
		for link in links:
			try:
				img = '<img height="176" width="320" src="%s " \
onerror="this.style.display=\'none\'" ' % (link)
				html.write(img + 'onclick="window.\
open(this.src)">' + '\n')
				url += 1
				print(f'[{url} / {len(links)}] Writing album \
pictures to .html file..', end='\r')
			except:
				#traceback.print_exc()
				continue

def main():
	global albums, a_num, r_n, d

	print('Starting to \
scrap albums..')

	get_albums()

	if len(albums) < 1:
		print('\nError...May not be actually a \
Twonky server or dead. Check.')
#		driver.quit()
#		exit(0)

	print('\n\n')
	for albm, total in d.items():
		print(f'Found album: {albm} :: {total} photos')
	print(f'\n\nTotal found {a_num} albums')
	print('\nTrying recursive scoping..\n')

	while r_n < 10:
		r_n += 1
		recursion()

	albums.append(f'http://{tw}\
/webbrowse#photo')

	counter = 0
	for album in albums:
		try:
			counter += 1
			get_links(album, counter)
		except:
			traceback.print_exc()
			time.sleep(1)
			continue

	html()
	print('\n')
	driver.quit()
	exit(0)

if __name__ == "__main__":
	main()
