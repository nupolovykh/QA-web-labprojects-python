import math, pytest
from functions import multiply, divide, distance, quadratic_equation, geometric_series_sum

# task 2. Tests. Nikita Polovykh 107б1
def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-1, 5) == -5
    assert multiply(0, 10) == 0
    assert multiply(-2, -3) == 6
    assert multiply(1.5, 2) == 3.0

def test_divide():
    assert divide(10, 2) == 5.0
    assert divide(5, -1) == -5.0
    assert divide(0, 10) == 0.0
    with pytest.raises(Exception):
        divide(1, 0)
    assert divide(7.5, 2.5) == 3.0

def test_distance():
    assert distance((0, 0), (3, 4)) == 5.0
    assert distance((1, 1), (1, 1)) == 0.0
    assert distance((0, 0), (0, 0)) == 0.0
    assert math.isclose(distance((-1, -1), (1, 1)), math.sqrt(8))
    assert distance((1, 2), (4, 6)) == 5.0

def test_quadratic_equation():
    assert quadratic_equation(1, -3, 2) == (2.0, 1.0)
    assert quadratic_equation(1, 2, 1) == (-1.0,)
    assert quadratic_equation(1, 0, -4) == (2.0, -2.0)
    with pytest.raises(Exception):
        quadratic_equation(1, 0, 4)
    assert quadratic_equation(2, 4, 2) == (-1.0,)

def test_geometric_series_sum():
    assert geometric_series_sum(2, 3, 4) == 80.0
    assert geometric_series_sum(1, 1, 5) == 5.0
    assert geometric_series_sum(5, 0, 10) == 5.0
    assert geometric_series_sum(1, -1, 4) == 0.0
    assert geometric_series_sum(3, 2, 3) == 21.0