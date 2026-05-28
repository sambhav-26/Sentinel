import json
import subprocess
from typing import Any, Dict, List


def run_bandit(target_path: str) -> List[Dict[str, Any]]:
	"""Run Bandit and return structured findings."""
	command = ["bandit", "-r", target_path, "-f", "json"]
	try:
		result = subprocess.run(
			command,
			capture_output=True,
			text=True,
			encoding="utf-8",
			errors="ignore",
			timeout=300,
			check=False,
		)
	except FileNotFoundError:
		print("Bandit not found. Install Bandit to enable scanning.")
		return []
	except subprocess.TimeoutExpired:
		print("Bandit scan timed out.")
		return []
	except OSError as exc:
		print(f"Bandit execution failed: {exc}")
		return []

	if result.returncode not in (0, 1):
		stderr = result.stderr.strip() if result.stderr else "Unknown error"
		print(f"Bandit failed: {stderr}")
		return []

	try:
		payload = json.loads(result.stdout or "{}")
		results = payload.get("results", [])
		return [_normalize_finding(item) for item in results]
	except json.JSONDecodeError:
		print("Bandit output was not valid JSON.")
		return []


def _normalize_finding(item: Dict[str, Any]) -> Dict[str, Any]:
	"""Normalize Bandit JSON output into the ScanAgent format."""
	path = item.get("filename", "")
	line = int(item.get("line_number", 0) or 0)
	severity = str(item.get("issue_severity", "MEDIUM")).upper()
	issue_text = item.get("issue_text", "Bandit finding")
	confidence = str(item.get("issue_confidence", "MEDIUM")).upper()
	code = (item.get("code", "") or "").strip()
	test_id = item.get("test_id", "")
	vuln_type = _map_bandit_type(test_id, issue_text, code)
	return {
		"file": path,
		"line": line,
		"severity": severity,
		"issue_text": issue_text,
		"confidence": confidence,
		"test_id": test_id,
		"code": code,
		"type": vuln_type,
	}


def _map_bandit_type(test_id: str, issue_text: str, code: str) -> str:
	blob = f"{test_id} {issue_text} {code}".lower()
	if "assert_used" in blob:
		return "Insecure Assertion Usage"
	if "sql" in blob and "inject" in blob:
		return "SQL Injection"
	if "shell" in blob and "subprocess" in blob:
		return "Command Injection"
	if "pickle" in blob or "deserialize" in blob:
		return "Dangerous Code Execution"
	if "md5" in blob or "sha1" in blob:
		return "Weak Cryptography"
	if "secret" in blob or "password" in blob or "hardcoded" in blob:
		return "Hardcoded Secret"
	return "Bandit Finding"
