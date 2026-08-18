from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Task 1: open python.org
driver.get("https://www.python.org/")
driver.maximize_window()
print('\n')

# Task 2: fetch the header image src
imageLink = driver.find_element(By.XPATH, '//h1//img').get_property('src')
print('<img> src => ' + imageLink)
print('\n')

# Task 3: fetch links from the "about" section
imageList = driver.find_elements(By.XPATH, '//*[@id="about"]//a')
for a in imageList:
    print('<a> href => ' + a.get_property('href'))

print('\n')

# Task 4: fetch widget titles
h2TextList = driver.find_elements(By.CSS_SELECTOR, '[class="widget-title"]')
for h2 in h2TextList:
    print('<h2> text => ' + h2.text)

print('\n')

# Task 5: fetch navigation menu links
aLinkList = driver.find_element(By.CSS_SELECTOR, '[class="navigation menu"]').find_elements(By.TAG_NAME, 'a')

for a in aLinkList:
    print('<a> href => ' + a.get_property('href'))

driver.quit()