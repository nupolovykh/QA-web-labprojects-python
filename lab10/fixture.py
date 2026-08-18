import pytest

# task 3-4. File & Fixture. Nikita Polovykh 107б1
@pytest.fixture
def text_file_content():
	with open('file.txt', 'r', encoding='utf-8') as file:
		content = file.read()
	return content