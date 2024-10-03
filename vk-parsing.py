from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import csv
import time

PATH = (r"E:\chromedriver-win64\chromedriver.exe")
service = Service(executable_path=PATH)
driver = webdriver.Chrome(service=service)

HREF = (r"https://vk.com/video")
driver.get(HREF)
driver.maximize_window()
print('\n')

try:
	# task 1. parse sections. Nikita Polovykh 107б1
	driver.get('https://vk.com/video')
	time.sleep(3)

	targets = ['For you', 'Trending']
	video_data = []
	slinks = []

	links = driver.find_elements(By.XPATH, "//a[contains(@class,'MenuList__item')]")

	target_set = set(targets)
	slinks = [link.get_attribute('href') for link in links if link.text in target_set]

	# task 2. parse info. Nikita Polovykh 107б1
	for slink in slinks:
		try:
			if(slink != HREF):
				driver.get(slink)

			buttons = driver.find_elements(By.XPATH, f"//a[contains(@class,'VideoCard__thumbLink')]")
			video_links = [button.get_attribute('href') for button in buttons]
            
			for link in video_links:
				driver.get(link)
				time.sleep(2)

				try:
					title = driver.find_element(By.XPATH, '//*[@id="mv_main_info"]/div/div/div[1]/div/div/div/div[1]/div/div/span/div/div/div').text

					views_date_str = driver.find_element(By.XPATH, '//*[@id="mv_main_info"]/div/div/div[1]/div/div/div/div[2]/div/div/span')
					views_date_list = views_date_str.text.split('·')
					views = views_date_list[0]
					date = views_date_list[1]

					likes = driver.find_element(By.XPATH, '//*[@id="mv_main_info"]/div/div/div[2]/div[2]/div/div[1]/span[2]').text
					channel_name = driver.find_element(By.XPATH, '//*[@id="mv_main_info"]/div/div/div[2]/div[1]/div[2]/div[1]/span/div/a').text
					subscribers = driver.find_element(By.XPATH, '//*[@id="mv_main_info"]/div/div/div[2]/div[1]/div[2]/div[2]/span').text

					video_data.append([title, views, likes, date, channel_name, subscribers])

				except Exception as video_error:
					print(f"Error retrieving data for {link}: {video_error}")

				driver.back()
				time.sleep(2)

		except Exception as section_error:
			print(f"Error retrieving links from {slink} section: {section_error}")

		driver.back()
finally:
    driver.quit()

# task 3. file filling. Nikita Polovykh 107б1
with open('video_data.csv', mode='w', newline='', encoding='utf-8') as file:
	writer = csv.writer(file)
	writer.writerow(["Title", "Views", "Likes", "Creation Date", "Channel Name", "Subscribers"])

	for data in video_data:
		writer.writerow(data)
