import math

# task 1. Functions. Nikita Polovykh 107б1
def multiply(a, b):
	return a * b

def divide(a, b):
	if b == 0:
		raise Exception
	return a / b

def distance(point1, point2):
	x1, y1 = point1
	x2, y2 = point2
	return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def quadratic_equation(a, b, c):
	discriminant = b**2 - 4*a*c
	if discriminant > 0:
		root1 = (-b + math.sqrt(discriminant)) / (2 * a)
		root2 = (-b - math.sqrt(discriminant)) / (2 * a)
		return (root1, root2)
	elif discriminant == 0:
		root = -b / (2 * a)
		return (root,)
	else:
		raise Exception

def geometric_series_sum(a, r, n):
	if n <= 0:
		return 0
	if r == 1:
		return a * n
	return a * (1 - r**n) / (1 - r)

# task 2. New functions. Nikita Polovykh 107б1
def words_quantity(str: str) -> int:
	spaces = str.count(" ")
	if str and (str[-1] == " "):
		return spaces
	else:
		return spaces + 1

def substring(str : str, a : int, b : int) -> str:
	return str[a:b]

def to_upper_case(str : str) -> str:
	return str.upper()
