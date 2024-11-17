import pytest, math
from functions import multiply, divide, distance, quadratic_equation, geometric_series_sum, words_quantity, substring, to_upper_case
from fixture import text_file_content

# task 5. TestMathClass. Nikita Polovykh 107б1
class TestMathFunctions:
	@pytest.mark.parametrize("a, b, expected", [
		(2, 3, 6),
		(-1, 10, -10),
		(0, 5, 0),
		(1.5, 2.0, 3.0),
		(-2, -3, 6),
	])
	def test_multiply(self, a, b, expected):
		assert multiply(a, b) == expected

	@pytest.mark.parametrize("a, b, expected", [
		(10, 2, 5.0),
		(5, -1, -5.0),
		(0, 10, 0.0),
		(7.5, 2.5, 3.0),
	])
	def test_divide(self, a, b, expected):
		if b == 0:
			with pytest.raises(Exception):
				divide(a, b)
		else:
			assert divide(a, b) == expected

	@pytest.mark.parametrize("point1, point2, expected", [
		((0, 0), (3, 4), 5.0),
		((1, 1), (1, 1), 0.0),
		((0, 0), (0, 0), 0.0),
		((-1, -1), (1, 1), math.sqrt(8)),
		((1, 2), (4, 6), 5.0),
	])
	def test_distance(self, point1, point2, expected):
		assert math.isclose(distance(point1, point2), expected)

	@pytest.mark.parametrize("a, b, c, expected", [
		(1, -3, 2, (2.0, 1.0)),
		(1, 2, 1, (-1.0,)),
		(1, 0, -4, (2.0, -2.0)),
		(1, 0, 4, None),
		(2, 4, 2, (-1.0,)),
	])
	def test_quadratic_equation(self, a, b, c, expected):
		if expected is None:
			with pytest.raises(Exception):
				quadratic_equation(a, b, c)
		else:
			assert quadratic_equation(a, b, c) == expected

	@pytest.mark.parametrize("a, r, n, expected", [
		(1, 0.5, 5, 1 * (1 - 0.5**5) / (1 - 0.5)),
		(2, 1, 3, 6),
		(3, 2, 4, 3 * (1 - 2**4) / (1 - 2)),
		(4, 0.1, 10, pytest.approx(4 * (1 - 0.1**10) / (1 - 0.1))),
		(5, -1, 3, 5 + (-5) + 5),
	])
	def test_geometric_series_sum(self, a, r, n, expected):
		assert pytest.approx(geometric_series_sum(a, r, n), 0.01) == expected
		

# task 6. TestTextClass. Nikita Polovykh 107б1
class TestTextFunctions:
	@pytest.mark.parametrize("count", [
		2,
	])
	def test_words_quantity(self, text_file_content : str, count: int)  -> None:
		assert words_quantity(text_file_content) == count

	@pytest.mark.parametrize("expected_upper", [
		"lyuboy text".upper(),
	])
	def test_to_upper_case(self, text_file_content : str, expected_upper : str)  -> None:
		assert to_upper_case(text_file_content) == expected_upper  

	@pytest.mark.parametrize("start, end, expected_substring", [
		(0, 1, "l"),
		(0, 2, "ly"),
		(0, 3, "lyu"),
		(3, 6, "boy"),
		(0, 11, "lyuboy text")
	])
	def test_substring(self, text_file_content : str, start : int, end : int, expected_substring : str) -> None:
		assert substring(text_file_content, start, end) == expected_substring