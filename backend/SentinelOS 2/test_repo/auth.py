API_KEY = "abcd123"
password = "admin123"


def authenticate(user_password: str) -> bool:
	return user_password == password
