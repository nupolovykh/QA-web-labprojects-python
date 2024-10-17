from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.common.keys import Keys
import asyncio
import time
import shutil

def open_new_tab(url):
	driver.switch_to.new_window('tab')
	driver.get(url)
	time.sleep(1)

def wiki_tabs_opener(num):
	driver.switch_to.window(driver.window_handles[num])
	random_url = driver.find_element(By.XPATH, '//*[@id="n-randompage"]/a').get_attribute('href')
	time.sleep(1)
	for _ in range(5):
		open_new_tab(random_url)



PATH = (r"E:\chromedriver-win64\chromedriver.exe")
service = Service(executable_path=PATH)
driver = webdriver.Chrome(service=service)

URL_CONVERTOR = (r"https://www.base64encode.org/")
URLS_WIKI = [(r"https://ru.wikipedia.org"), (r"https://en.wikipedia.org")]

# task 1. Open 3 separate tabs. Nikita Polovykh 107б1
driver.get(URL_CONVERTOR)
for url in URLS_WIKI:
	open_new_tab(url)

# task 2. Open 5 separate random wiki pages. Nikita Polovykh 107б1
wiki_tabs_opener(1)
time.sleep(10)

wiki_tabs_opener(2)
time.sleep(10)

# task 3. Fetch all titles of opened random tabs. Nikita Polovykh 107б1

titles = []
for num in range(3, 13):
	try:
		driver.switch_to.window(driver.window_handles[num])
		title = driver.find_element(By.CLASS_NAME, 'mw-page-title-main').text
		titles.append(title)
	except Exception:
		try:
			title = driver.find_element(By.XPATH, '//*[@id="firstHeading"]/i').text
			titles.append(title)
		except Exception:
			print("Page of error - " + str(num))
			print("Url of error - " + driver.current_url)

for _ in range(10):
	driver.switch_to.window(driver.window_handles[3])
	driver.close()


time.sleep(3)

# task 4. Push and Fetch all titles of opened random tabs. Nikita Polovykh 107б1

driver.switch_to.window(driver.window_handles[0])

titles_union = (' ').join(titles)
driver.find_element(By.ID, 'input').send_keys(titles_union)
driver.find_element(By.ID, 'submit_text').click()
titles_union_base = driver.find_element(By.ID, 'output').text

print(titles_union)
print(titles_union_base)

driver.quit()