import os

def run_user_code(user_input: str) -> None:
	# Insecure demo only: dangerous eval usage
	eval(user_input)


def run_system_command(user_input: str) -> None:
	# Insecure demo only: command injection risk
	os.system(user_input)
