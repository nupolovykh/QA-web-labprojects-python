from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

PATH = (r"E:\chromedriver-win64\chromedriver.exe")
service = Service(executable_path=PATH)
driver = webdriver.Chrome(service=service)

#first task		Nikita Polovykh 107б1
driver.get("https://www.python.org/")
driver.maximize_window()
print('\n')

#second task		Nikita Polovykh 107б1
imageLink = driver.find_element(By.XPATH, '//h1//img').get_property('src')
print('<img> src => ' + imageLink)
print('\n')

#third task		Nikita Polovykh 107б1
imageList = driver.find_elements(By.XPATH, '//*[@id="about"]//a')
for a in imageList:
    print('<a> href => ' + a.get_property('href'))
    
print('\n')
    
#fourth task		Nikita Polovykh 107б1
h2TextList = driver.find_elements(By.CSS_SELECTOR, '[class="widget-title"]')
for h2 in h2TextList:
    print('<h2> text => ' + h2.text)

print('\n')

#fifth task		Nikita Polovykh 107б1
aLinkList = driver.find_element(By.CSS_SELECTOR, '[class="navigation menu"]').find_elements(By.TAG_NAME, 'a')

for a in aLinkList:
    print('<a> href => ' + a.get_property('href'))

driver.quit()