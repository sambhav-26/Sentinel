import json
import os
import re
from pathlib import Path


SUPPORTED_EXTENSIONS = {".py", ".js", ".env", ".json", ".txt", ".yaml", ".yml"}

VULN_RULES = [
	{
		"name": "Dangerous eval() usage",
		"severity": "Critical",
		"patterns": [re.compile(r"\beval\s*\(")],
	},
	{
		"name": "Hardcoded Password",
		"severity": "High",
		"patterns": [
			re.compile(r"\bpassword\s*=\s*[\"']"),
			re.compile(r"\bpassword\s*=\s*[^\s#]+"),
		],
	},
	{
		"name": "Hardcoded API Key",
		"severity": "High",
		"patterns": [
			re.compile(r"\b(api_key|apikey|apiKey)\s*=\s*[\"']"),
			re.compile(r"\b(api_key|apikey|apiKey)\s*=\s*[^\s#]+"),
		],
	},
	{
		"name": "SQL Injection Risk",
		"severity": "Critical",
		"patterns": [
			re.compile(r"SELECT\s+.+\s+FROM\s+.+\+\s*\w+", re.IGNORECASE),
			re.compile(r"\bquery\s*=\s*[\"'].*SELECT.*[\"']\s*\+\s*\w+", re.IGNORECASE),
			re.compile(r"f[\"'].*SELECT.*\{.+\}.*[\"']", re.IGNORECASE),
		],
	},
	{
		"name": "Dangerous os.system() usage",
		"severity": "Critical",
		"patterns": [re.compile(r"\bos\.system\s*\(")],
	},
	{
		"name": "Unsafe subprocess usage",
		"severity": "Critical",
		"patterns": [
			re.compile(r"\bsubprocess\.(call|run|Popen)\s*\(.*shell\s*=\s*True", re.IGNORECASE),
		],
	},
]

CWE_MAP = {
	"Dangerous eval() usage": "CWE-94",
	"SQL Injection Risk": "CWE-89",
	"Hardcoded Password": "CWE-798",
	"Dangerous os.system() usage": "CWE-78",
	"Unsafe subprocess usage": "CWE-78",
	"Hardcoded API Key": "CWE-798",
}

EXPLOITABILITY_MAP = {
	"Critical": 9.8,
	"High": 8.2,
	"Medium": 5.4,
	"Low": 2.1,
}


def _is_supported_file(file_name: str) -> bool:
	if file_name == ".env":
		return True
	return Path(file_name).suffix.lower() in SUPPORTED_EXTENSIONS


def _scan_file(file_path: str, repo_root: str) -> list:
	findings = []
	try:
		with open(file_path, "r", encoding="utf-8", errors="ignore") as handle:
			for line_number, line in enumerate(handle, start=1):
				for rule in VULN_RULES:
					if any(pattern.search(line) for pattern in rule["patterns"]):
						rel_path = os.path.relpath(file_path, repo_root)
						rel_path = rel_path.replace(os.sep, "/")
						findings.append(
							{
								"file": rel_path,
								"line": line_number,
								"severity": rule["severity"],
								"cwe": CWE_MAP.get(rule["name"], "CWE-000"),
								"exploitability": EXPLOITABILITY_MAP.get(rule["severity"], 0.0),
								"vulnerability": rule["name"],
								"code_snippet": line.strip(),
							}
						)
						break
	except (OSError, UnicodeError):
		return []

	return findings


def run_scan(repository_path: str) -> dict:
	"""Scan a repository and save results to scanner_output.json."""
	results = {"repository": repository_path, "total_findings": 0, "findings": []}
	findings_counter = 0
	for root, _, files in os.walk(repository_path):
		for file_name in files:
			if not _is_supported_file(file_name):
				continue
			file_path = os.path.join(root, file_name)
			file_findings = _scan_file(file_path, repository_path)
			for finding in file_findings:
				findings_counter += 1
				finding["id"] = f"VULN-{findings_counter:03d}"
				results["findings"].append(finding)

	results["total_findings"] = len(results["findings"])

	output_path = Path(__file__).parent / "scanner_output.json"
	with output_path.open("w", encoding="utf-8") as handle:
		json.dump(results, handle, indent=2)
	return results


if __name__ == "__main__":
	repo_path = input("Enter repository path: ").strip()
	data = run_scan(repo_path)
	print(json.dumps(data, indent=2))
