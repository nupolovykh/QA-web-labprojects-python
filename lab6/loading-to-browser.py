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

PATH = (r"E:\chromedriver-win64\chromedriver.exe")
service = Service(executable_path=PATH)
driver = webdriver.Chrome(service=service)

URL_CONTEX = (r"https://the-internet.herokuapp.com/context_menu")
URL_UPLOAD = (r"https://the-internet.herokuapp.com/upload")

driver.get(URL_CONTEX)
driver.maximize_window()

# task 1. Summon and submit context menu. Nikita Polovykh 107б1
area = driver.find_element(By.ID, "hot-spot")
action = ActionChains(driver)
action.context_click(area).perform()
time.sleep(3)

# this snippet break the app completely for some reason + can not make screenshot with context
 
# try:
# 	driver.get_screenshot_as_file("context-file.png")
# except Exception:
# 	print("Can not make screenshot!")

alert = driver.switch_to.alert
print(alert.text)
alert.accept()

time.sleep(10)

# task 2. Uploading file bliendly. Nikita Polovykh 107б1

driver.get(URL_UPLOAD)

#area = driver.find_element(By.ID, "drag-drop-upload").click()
upload_file = (r"here\was\my\path\textfile.txt")

file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
file_input.send_keys(upload_file)
driver.find_element(By.ID, "file-submit").click()
time.sleep(3)

try:
	driver.get_screenshot_as_file("context-file.png")
except Exception:
	print("Can not make screenshot!")

time.sleep(10)
driver.quit()