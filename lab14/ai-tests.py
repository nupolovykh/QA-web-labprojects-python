import time
from datetime import datetime, timezone

import pytest
from ci_nsu import CiNsuNewsPage


# Task 3: fixture wrapping the POM class
@pytest.fixture
def news_page():
    page = CiNsuNewsPage()
    page.offset_date_after(datetime(2022, 12, 1, tzinfo=timezone.utc))
    page.offset_date_before(datetime(2024, 12, 1, tzinfo=timezone.utc))
    time.sleep(2)
    page.submit_offset()
    return page

# Task 3.5: tests exercising the POM helpers
@pytest.mark.parametrize("expected_title", ["Все новости"])
def test_verify_title_before(news_page, expected_title):
    assert expected_title == news_page.get_page_title()

@pytest.mark.parametrize("expected_title", ["Олимпиада по математике"])
def test_verify_first_news_title(news_page, expected_title):
    newslist = news_page.fetch_the_news_info_by("name")
    assert expected_title == newslist[0].text

@pytest.mark.parametrize("expected_title", ["Изменение стоимости проживания в общежитии ВКИ НГУ"])
def test_verify_last_news_title(news_page, expected_title):
    newslist = news_page.fetch_the_news_info_by("name")
    assert expected_title == newslist[-1].text

@pytest.mark.parametrize("expected_first, expected_last", [
    (datetime(2022, 12, 1, tzinfo=timezone.utc), datetime(2024, 12, 1, tzinfo=timezone.utc)),
])
def test_verify_first_and_last_news_dates(news_page, expected_first, expected_last):
    datelist = news_page.fetch_the_news_info_by("date")
    first_date = datetime.strptime(datelist[0].text, "%d.%m.%Y").replace(tzinfo=timezone.utc)
    last_date = datetime.strptime(datelist[-1].text, "%d.%m.%Y").replace(tzinfo=timezone.utc)
    assert (first_date >= expected_first and last_date <= expected_last)

@pytest.mark.parametrize("expected_first, expected_last", [
    (datetime(2021, 12, 1, tzinfo=timezone.utc), datetime(2023, 10, 1, tzinfo=timezone.utc)),
])
def test_verify_first_and_last_news_dates_failure(news_page, expected_first, expected_last):
    datelist = news_page.fetch_the_news_info_by("date")
    first_date = datetime.strptime(datelist[0].text, "%d.%m.%Y").replace(tzinfo=timezone.utc)
    last_date = datetime.strptime(datelist[-1].text, "%d.%m.%Y").replace(tzinfo=timezone.utc)
    assert not (first_date < expected_first or last_date > expected_last)


@pytest.mark.parametrize("expected_title", ["Все новости"])
def test_verify_title_after(news_page, expected_title):
    assert expected_title == news_page.get_page_title()
