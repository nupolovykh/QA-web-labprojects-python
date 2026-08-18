import time
from datetime import datetime
from typing import ClassVar

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


# Task 1: Page Object Model class
class CiNsuNewsPage:

	URL = (r"https://ci.nsu.ru/news/")
	news: ClassVar[list] = []

	def __init__(self):
		service = Service(ChromeDriverManager().install())
		self.driver = webdriver.Chrome(service=service)
		self.driver.get(self.URL)

		forms = self.driver.find_elements(By.CLASS_NAME, "col-xs-6")
		self.after = forms[0].find_element(By.TAG_NAME, "input")
		self.before = forms[1].find_element(By.TAG_NAME, "input")

		self.submit = self.driver.find_element(By.CLASS_NAME, "btn-success")

	# Task 2: page interaction helpers

	# dates before inserted param
	def get_page_title(self) -> str:
		return self.driver.find_element(By.CLASS_NAME, "news-detail-row").find_element(By.TAG_NAME, "h1").text
	
	# dates before inserted param
	def offset_date_before(self, date : datetime):
		value = date.strftime('%d.%m.%Y')
		self.before.send_keys(value)

	# dates after inserted param
	def offset_date_after(self, date  : datetime):
		value = date.strftime('%d.%m.%Y')
		self.after.send_keys(value)

	def submit_offset(self):
		self.submit.click()
		
		while True:
			btn = self.load_available()
			if btn is None:
				break
			btn.click()
			time.sleep(2)

	def fetch_the_news_info_by(self, field : str) -> list:
		cards = self.driver.find_element(By.CLASS_NAME, "news-list")
		return cards.find_elements(By.CLASS_NAME, field)
	
	def load_available(self):
		try:
			btn = self.driver.find_element(By.CLASS_NAME, "moreNewsList")
			return btn
		except NoSuchElementException:
			return None