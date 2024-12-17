from datetime import datetime
import time, pytest

from ci_nsu import CiNsuNewsPage

class CiNsuNewsPage_Test:

	def __init__(self):
		self.page = CiNsuNewsPage()

		self.page.offset_date_after(datetime(2022, 12, 1))
		self.page.offset_date_before(datetime(2024, 12, 1))
		time.sleep(2)

		self.page.submit_offset()

	@pytest.mark.parametrize("title", ["Все новости"])
	def verify_title_before(self, title):
		assert title == self.page.get_page_title()

	@pytest.mark.parametrize("new_title", ["Олимпиада по математике"])
	def verify_first_new_title(self, new_title):
		newslist = self.page.fetch_the_news_info_by("name")
		assert new_title == newslist[0].text

	@pytest.mark.parametrize("new_title", ["Изменение стоимости проживания в общежитии ВКИ НГУ"])
	def verify_last_new_title(self, new_title):
		newslist = self.page.fetch_the_news_info_by("name")
		assert new_title == newslist[len(newslist) - 1].text

	@pytest.mark.parametrize("first", "last", [{datetime(2022, 12, 1), datetime(2024, 12, 1)}])
	def verify_first_and_last_news_dates(self, first_value, second_value):
		datelist = self.page.fetch_the_news_info_by("date")

		first_date = datetime.strptime(datelist[0].text, "%d.%m.%Y")
		last_date = datetime.strptime(datelist[len(datelist) - 1].text, "%d.%m.%Y")

		assert (first_date == first_value and last_date == second_value)

	@pytest.mark.parametrize("title", ["Все новости"])
	def verify_title_after(self, title):
		assert title == self.page.get_page_title()