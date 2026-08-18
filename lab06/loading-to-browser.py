from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import UnexpectedAlertPresentException, NoAlertPresentException
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import asyncio
import os
import time
import shutil

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

URL_CONTEX = (r"https://the-internet.herokuapp.com/context_menu")
URL_UPLOAD = (r"https://the-internet.herokuapp.com/upload")

driver.get(URL_CONTEX)
driver.maximize_window()

# Task 1: summon and accept the context menu
area = driver.find_element(By.ID, "hot-spot")
action = ActionChains(driver)
action.context_click(area).perform()
time.sleep(3)

# this snippet break the app completely for some reason + can not make screenshot with context
 
# try:
# 	driver.get_screenshot_as_file("docs/screenshot.png")
# except Exception:
# 	print("Can not make screenshot!")

alert = driver.switch_to.alert
print(alert.text)
alert.accept()

time.sleep(10)

# Task 2: upload a file

driver.get(URL_UPLOAD)

#area = driver.find_element(By.ID, "drag-drop-upload").click()
upload_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "textfile.txt")

file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
file_input.send_keys(upload_file)
driver.find_element(By.ID, "file-submit").click()
time.sleep(3)

try:
	screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs", "screenshot.png")
	driver.get_screenshot_as_file(screenshot_path)
except Exception:
	print("Can not make screenshot!")

time.sleep(10)
driver.quit()