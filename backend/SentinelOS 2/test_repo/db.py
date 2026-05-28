def get_user_by_id(user_input: str) -> str:
	query = "SELECT * FROM users WHERE id = " + user_input
	return query
