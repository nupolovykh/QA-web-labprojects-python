import pytest


# Task 3-4: file-backed fixture
@pytest.fixture
def text_file_content():
	with open('file.txt', 'r', encoding='utf-8') as file:
		content = file.read()
	return content