import json
import subprocess
from typing import Any, Dict, List


def run_semgrep(target_path: str) -> List[Dict[str, Any]]:
	"""Run Semgrep CLI and return structured findings."""
	command = ["semgrep", "--config", "auto", "--json", target_path]
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
		print("Semgrep not found. Install Semgrep to enable scanning.")
		return []
	except subprocess.TimeoutExpired:
		print("Semgrep scan timed out.")
		return []
	except OSError as exc:
		print(f"Semgrep execution failed: {exc}")
		return []

	if result.returncode not in (0, 1):
		stderr = result.stderr.strip() if result.stderr else "Unknown error"
		print(f"Semgrep failed: {stderr}")
		return []

	try:
		payload = json.loads(result.stdout or "{}")
		results = payload.get("results", [])
		return [_normalize_finding(item) for item in results]
	except json.JSONDecodeError:
		print("Semgrep output was not valid JSON.")
		return []


def _normalize_finding(item: Dict[str, Any]) -> Dict[str, Any]:
	"""Normalize Semgrep JSON output into the ScanAgent format."""
	path = item.get("path", "")
	start = item.get("start", {}) or {}
	line = int(start.get("line", 0) or 0)
	raw_severity = str(item.get("extra", {}).get("severity", "MEDIUM")).upper()
	severity = _map_semgrep_severity(raw_severity)
	rule_id = item.get("check_id", "")
	message = item.get("extra", {}).get("message", "Semgrep finding")
	code = _extract_semgrep_code(item)
	vuln_type = _map_semgrep_type(rule_id, message, code)
	return {
		"file": path,
		"line": line,
		"severity": severity,
		"rule_id": rule_id,
		"message": message,
		"code": code,
		"type": vuln_type,
	}


def _map_semgrep_severity(value: str) -> str:
	if value == "INFO":
		return "LOW"
	if value == "WARNING":
		return "MEDIUM"
	if value == "ERROR":
		return "HIGH"
	return value if value in {"LOW", "MEDIUM", "HIGH", "CRITICAL"} else "MEDIUM"


def _map_semgrep_type(rule_id: str, message: str, code: str) -> str:
	blob = f"{rule_id} {message} {code}".lower()
	if "sql" in blob and "inject" in blob:
		return "SQL Injection"
	if "xss" in blob:
		return "XSS"
	if "md5" in blob or "sha1" in blob:
		return "Weak Cryptography"
	if "eval" in blob or "exec" in blob:
		return "Dangerous Code Execution"
	if "shell=true" in blob or "os.system" in blob or "subprocess" in blob:
		return "Command Injection"
	if "secret" in blob or "apikey" in blob or "api key" in blob or "token" in blob:
		return "Hardcoded Secret"
	return "Semgrep Finding"


def _extract_semgrep_code(item: Dict[str, Any]) -> str:
	lines = item.get("extra", {}).get("lines")
	if isinstance(lines, list):
		return "\n".join(str(line) for line in lines).strip()
	if isinstance(lines, str) and lines.strip():
		return lines.strip()
	match = item.get("extra", {}).get("message", "")
	return str(match).strip()
