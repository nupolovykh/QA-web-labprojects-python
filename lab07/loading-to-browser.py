import time

from selenium import webdriver
from selenium.common.exceptions import (
	NoSuchElementException,
	StaleElementReferenceException,
	TimeoutException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


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



service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

URL_CONVERTOR = (r"https://www.base64encode.org/")
URLS_WIKI = [(r"https://ru.wikipedia.org"), (r"https://en.wikipedia.org")]

# Task 1: open 3 separate tabs
driver.get(URL_CONVERTOR)

# base64encode.org shows a cookie-consent overlay (Quantcast Choice) a few
# seconds after load, which blocks the #input textarea for the rest of the
# tab's life once it appears. Dismiss it now while we're on the tab, since
# Task 4 comes back to this same tab without reloading.
try:
	WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "accept-btn"))).click()
except TimeoutException:
	pass

for url in URLS_WIKI:
	open_new_tab(url)

# Task 2: open 5 separate random wiki pages
wiki_tabs_opener(1)
time.sleep(10)

wiki_tabs_opener(2)
time.sleep(10)

# Task 3: fetch all titles of opened random tabs

titles = []
for num in range(3, 13):
	try:
		driver.switch_to.window(driver.window_handles[num])
		title = driver.find_element(By.CLASS_NAME, 'mw-page-title-main').text
		titles.append(title)
	except NoSuchElementException:
		try:
			title = driver.find_element(By.XPATH, '//*[@id="firstHeading"]/i').text
			titles.append(title)
		except NoSuchElementException:
			print("Page of error - " + str(num))
			print("Url of error - " + driver.current_url)

for _ in range(10):
	driver.switch_to.window(driver.window_handles[3])
	driver.close()


time.sleep(3)

# Task 4: submit and fetch back the joined titles

driver.switch_to.window(driver.window_handles[0])

titles_union = (' ').join(titles)
driver.find_element(By.ID, 'input').send_keys(titles_union)
driver.find_element(By.ID, 'submit_text').click()
# The page re-renders #output when encoding finishes, which stales any
# WebElement obtained before the click - re-querying inside the wait
# condition (instead of a single find_element right after) avoids that.
titles_union_base = WebDriverWait(driver, 10, ignored_exceptions=(StaleElementReferenceException,)).until(
	lambda d: d.find_element(By.ID, 'output').text or False
)

print(titles_union)
print(titles_union_base)

driver.quit()