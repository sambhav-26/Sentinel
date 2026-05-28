import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from utils.cwe_mapping import get_cwe_mapping


@dataclass
class ScanFinding:
	"""Normalized vulnerability record for ScanAgent output."""

	vulnerability_id: str
	type: str
	severity: str
	confidence: float
	cwe_id: str
	owasp_category: str
	file_path: str
	file_name: str
	line_number: int
	column_number: int
	language: str
	code_snippet: str
	description: str
	attack_surface: str
	affected_component: str
	detection_source: List[str]
	detected_at: str


class ScanAgent:
	"""Repository scanning agent that produces structured vulnerability JSON."""

	SUPPORTED_EXTENSIONS = {
		".py",
		".js",
		".ts",
		".jsx",
		".tsx",
		".java",
		".go",
		".php",
		".rb",
		".env",
		".json",
		".yaml",
		".yml",
		".xml",
		".ini",
		".toml",
		".txt",
	}
	SPECIAL_FILENAMES = {
		"dockerfile",
		"docker-compose.yml",
		"docker-compose.yaml",
		"requirements.txt",
		"package.json",
		"package-lock.json",
		"yarn.lock",
		"pom.xml",
		"build.gradle",
	}
	IGNORE_DIRS = {"node_modules", "venv", "__pycache__", ".git", "build", "dist"}

	def __init__(self) -> None:
		self._counter = 0
		self._logger = logging.getLogger("sentinelos.scan")
		if not self._logger.handlers:
			logging.basicConfig(level=logging.INFO, format="[ScanAgent] %(message)s")

	def scan_repository(self, path: str) -> dict:
		"""Scan a repository or single file and return structured JSON output."""
		repo_path = Path(path).expanduser().resolve()
		scan_id = self._build_scan_id()
		start_time = datetime.utcnow().isoformat(timespec="seconds") + "Z"

		self._logger.info("Scan started: %s", repo_path)
		vulnerabilities: List[ScanFinding] = []
		total_files_scanned = 0

		for file_path in self._iter_files(repo_path):
			total_files_scanned += 1
			self._logger.info("Scanning file: %s", file_path)
			vulnerabilities.extend(self._scan_file(file_path))

		bandit_results = self._run_bandit(repo_path)
		vulnerabilities.extend(self._normalize_tool_findings(bandit_results, "Bandit"))
		vulnerabilities = self._dedupe_findings(vulnerabilities)

		output = {
			"scan_metadata": {
				"scan_id": scan_id,
				"repository_name": repo_path.name,
				"scan_timestamp": start_time,
				"scanner_version": "1.0",
			},
			"scan_summary": self._build_summary(total_files_scanned, vulnerabilities),
			"vulnerabilities": [self._as_dict(v) for v in vulnerabilities],
		}

		self._save_scan_output(output)
		self._logger.info("Scan completed: %s", scan_id)
		return output

	def _iter_files(self, path: Path) -> Iterable[Path]:
		if path.is_file():
			if self._is_scannable(path):
				yield path
			return

		for root, dirs, files in os.walk(path):
			dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
			for name in files:
				file_path = Path(root) / name
				if self._is_scannable(file_path):
					yield file_path

	def _is_scannable(self, path: Path) -> bool:
		name = path.name.lower()
		if name in self.SPECIAL_FILENAMES or name == ".env":
			return True
		return path.suffix.lower() in self.SUPPORTED_EXTENSIONS

	def _scan_file(self, file_path: Path) -> List[ScanFinding]:
		findings: List[ScanFinding] = []
		content = self._read_text(file_path)
		if content is None:
			return findings

		language = self._language_from_path(file_path)
		for line_number, line in enumerate(content.splitlines(), start=1):
			findings.extend(self._detect_line_issues(file_path, language, line_number, line))

		if file_path.name.lower() in {"requirements.txt", "package.json", "pom.xml", "build.gradle"}:
			findings.extend(self._detect_dependency_issues(file_path, content))
		if file_path.name.lower() in {"dockerfile", "docker-compose.yml", "docker-compose.yaml"}:
			findings.extend(self._detect_infra_issues(file_path, content))

		return findings

	def _detect_line_issues(
		self,
		file_path: Path,
		language: str,
		line_number: int,
		line: str,
	) -> List[ScanFinding]:
		results: List[ScanFinding] = []
		line_stripped = line.strip()
		if not line_stripped or line_stripped.startswith("#") or line_stripped.startswith("//"):
			return results
		if line_stripped.startswith("import ") or line_stripped.startswith("from "):
			return results

		line_lower = line.lower()
		if "select" in line_lower and "+" in line_lower:
			results.append(self._build_finding(
				"SQL Injection",
				"CRITICAL",
				0.9,
				file_path,
				line_number,
				line,
				"Unsanitized input concatenated into SQL query.",
				"Authentication API",
				"Database Query",
				"Heuristic",
			))
		if "os.system(" in line_lower or (
			"subprocess." in line_lower and "(" in line_lower and "shell=true" in line_lower
		):
			results.append(self._build_finding(
				"Command Injection",
				"HIGH",
				0.75,
				file_path,
				line_number,
				line,
				"Potential command execution with untrusted input.",
				"System Command",
				"Command Execution",
				"Heuristic",
			))
		if "eval(" in line_lower or "exec(" in line_lower or "pickle.loads(" in line_lower:
			results.append(self._build_finding(
				"Dangerous Code Execution",
				"HIGH",
				0.7,
				file_path,
				line_number,
				line,
				"Dynamic code execution or unsafe deserialization.",
				"Runtime Execution",
				"Execution Engine",
				"Heuristic",
			))
		if "password" in line_lower and "=" in line_lower:
			results.append(self._build_finding(
				"Hardcoded Password",
				"HIGH",
				0.85,
				file_path,
				line_number,
				line,
				"Hardcoded password detected in source or config.",
				"Configuration",
				"Credential Storage",
				"Heuristic",
			))
		if "jwt_secret" in line_lower or "secret_key" in line_lower:
			results.append(self._build_finding(
				"Weak JWT Secret",
				"HIGH",
				0.8,
				file_path,
				line_number,
				line,
				"Potential weak or hardcoded JWT secret.",
				"Authentication",
				"Token Signing",
				"Heuristic",
			))
		if any(key in line_lower for key in ["api_key", "secret", "token"]) and "=" in line_lower:
			results.append(self._build_finding(
				"Hardcoded Secret",
				"HIGH",
				0.8,
				file_path,
				line_number,
				line,
				"Potential hardcoded secret detected in code or config.",
				"Configuration",
				"Secrets Management",
				"Heuristic",
			))
		if "debug" in line_lower and "true" in line_lower:
			results.append(self._build_finding(
				"Debug Mode Enabled",
				"LOW",
				0.6,
				file_path,
				line_number,
				line,
				"Debug mode enabled in configuration.",
				"Configuration",
				"Runtime Settings",
				"Heuristic",
			))
		if "innerhtml" in line_lower or "dangerouslysetinnerhtml" in line_lower:
			results.append(self._build_finding(
				"XSS",
				"MEDIUM",
				0.55,
				file_path,
				line_number,
				line,
				"Potential HTML injection into DOM.",
				"Web UI",
				"Client Rendering",
				"Heuristic",
			))

		return results

	def _detect_dependency_issues(self, file_path: Path, content: str) -> List[ScanFinding]:
		results: List[ScanFinding] = []
		for line_number, line in enumerate(content.splitlines(), start=1):
			if "==" not in line and "@" not in line and line.strip() and not line.strip().startswith("#"):
				results.append(self._build_finding(
					"Unpinned Dependency",
					"LOW",
					0.4,
					file_path,
					line_number,
					line,
					"Dependency version is not pinned.",
					"Dependency",
					"Dependency Management",
					"Heuristic",
				))
		return results

	def _detect_infra_issues(self, file_path: Path, content: str) -> List[ScanFinding]:
		results: List[ScanFinding] = []
		for line_number, line in enumerate(content.splitlines(), start=1):
			line_lower = line.lower()
			if "privileged:" in line_lower and "true" in line_lower:
				results.append(self._build_finding(
					"Privileged Container",
					"HIGH",
					0.7,
					file_path,
					line_number,
					line,
					"Container running with privileged permissions.",
					"Infrastructure",
					"Container Runtime",
					"Heuristic",
				))
			if "hostnetwork" in line_lower and "true" in line_lower:
				results.append(self._build_finding(
					"Host Network Exposure",
					"MEDIUM",
					0.6,
					file_path,
					line_number,
					line,
					"Container uses host network namespace.",
					"Infrastructure",
					"Network",
					"Heuristic",
				))
		return results

	def _run_bandit(self, path: Path) -> List[Dict[str, object]]:
		try:
			from tools.bandit_runner import run_bandit
			return run_bandit(str(path))
		except Exception as exc:
			self._logger.warning("Bandit failed: %s", exc)
			return []

	def _normalize_tool_findings(self, findings: List[Dict[str, object]], source: str) -> List[ScanFinding]:
		normalized: List[ScanFinding] = []
		for item in findings:
			file_path = Path(str(item.get("file", "")))
			line_number = int(item.get("line", 0) or 0)
			severity = self._normalize_severity(str(item.get("severity", "MEDIUM")), source)
			description = str(item.get("message", item.get("issue_text", "Tool-detected issue.")))
			scan_type = self._map_tool_type(item)
			code = str(item.get("code", ""))
			if self._is_import_only_subprocess(scan_type, code):
				continue
			confidence = self._normalize_confidence(item, source)
			normalized.append(
				self._build_finding(
					scan_type,
					severity,
					confidence,
					file_path,
					line_number,
					code,
					description,
					"Tool",
					"Tool",
					source,
				)
			)
		return normalized

	def _is_import_only_subprocess(self, vuln_type: str, code: str) -> bool:
		if vuln_type != "Command Injection":
			return False
		code_line = code.strip().lower()
		return code_line in {"import subprocess", "from subprocess import"}

	def _map_tool_type(self, item: Dict[str, object]) -> str:
		vuln_type = str(item.get("type", "Tool Finding"))
		if vuln_type not in {"Semgrep Finding", "Bandit Finding", "Tool Finding"}:
			return vuln_type
		rule_id = str(item.get("rule_id", ""))
		test_id = str(item.get("test_id", ""))
		message = str(item.get("message", item.get("issue_text", "")))
		code = str(item.get("code", ""))
		blob = f"{rule_id} {test_id} {message} {code}".lower()
		if "sql" in blob and "inject" in blob:
			return "SQL Injection"
		if "xss" in blob:
			return "XSS"
		if "md5" in blob or "sha1" in blob:
			return "Weak Cryptography"
		if "eval" in blob or "exec" in blob or "pickle" in blob:
			return "Dangerous Code Execution"
		if "shell=true" in blob or "os.system" in blob or "subprocess" in blob:
			return "Command Injection"
		if "secret" in blob or "password" in blob or "token" in blob:
			return "Hardcoded Secret"
		return "Tool Finding"

	def _build_finding(
		self,
		finding_type: str,
		severity: str,
		confidence: float,
		file_path: Path,
		line_number: int,
		code_snippet: str,
		description: str,
		attack_surface: str,
		affected_component: str,
		detection_source: str,
	) -> ScanFinding:
		self._counter += 1
		vuln_id = f"VULN-{self._counter:04d}"
		cwe_id, owasp = get_cwe_mapping(finding_type)
		now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
		sources = [detection_source] if isinstance(detection_source, str) else list(detection_source)
		return ScanFinding(
			vulnerability_id=vuln_id,
			type=finding_type,
			severity=severity,
			confidence=round(float(confidence), 2),
			cwe_id=cwe_id,
			owasp_category=owasp,
			file_path=str(file_path),
			file_name=file_path.name,
			line_number=line_number,
			column_number=self._column_number(code_snippet),
			language=self._language_from_path(file_path),
			code_snippet=code_snippet.strip(),
			description=description,
			attack_surface=attack_surface,
			affected_component=affected_component,
			detection_source=sources,
			detected_at=now,
		)

	def _build_scan_id(self) -> str:
		stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
		return f"SCAN-{stamp}"

	def _build_summary(self, total_files: int, vulns: List[ScanFinding]) -> dict:
		summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
		for vuln in vulns:
			key = vuln.severity.lower()
			if key in summary:
				summary[key] += 1
		return {
			"total_files_scanned": total_files,
			"total_vulnerabilities": len(vulns),
			"critical": summary["critical"],
			"high": summary["high"],
			"medium": summary["medium"],
			"low": summary["low"],
		}

	def _language_from_path(self, path: Path) -> str:
		suffix = path.suffix.lower()
		mapping = {
			".py": "Python",
			".js": "JavaScript",
			".ts": "TypeScript",
			".jsx": "JavaScript",
			".tsx": "TypeScript",
			".java": "Java",
			".go": "Go",
			".php": "PHP",
			".rb": "Ruby",
			".json": "JSON",
			".yaml": "YAML",
			".yml": "YAML",
			".xml": "XML",
			".ini": "INI",
			".toml": "TOML",
		}
		return mapping.get(suffix, "Text")

	def _read_text(self, file_path: Path) -> Optional[str]:
		try:
			data = file_path.read_bytes()
			if b"\x00" in data:
				return None
			return data.decode("utf-8", errors="ignore")
		except OSError:
			self._logger.warning("Failed to read file: %s", file_path)
			return None

	def _normalize_severity(self, value: str, source: str) -> str:
		severity = value.upper()
		if source == "Semgrep":
			if severity == "INFO":
				return "LOW"
			if severity == "WARNING":
				return "MEDIUM"
			if severity == "ERROR":
				return "HIGH"
		if source == "Bandit" and severity in {"LOW", "MEDIUM", "HIGH"}:
			return severity
		return severity if severity in {"LOW", "MEDIUM", "HIGH", "CRITICAL"} else "MEDIUM"

	def _normalize_confidence(self, item: Dict[str, object], source: str) -> float:
		if source == "Bandit":
			conf = str(item.get("confidence", "MEDIUM")).upper()
			return {"HIGH": 0.85, "MEDIUM": 0.65, "LOW": 0.45}.get(conf, 0.6)
		if source == "Semgrep":
			return 0.75
		return 0.6

	def _column_number(self, snippet: str) -> int:
		return max(1, (snippet.find("(") + 1) if "(" in snippet else 1)

	def _dedupe_findings(self, findings: List[ScanFinding]) -> List[ScanFinding]:
		index: Dict[Tuple[str, str], ScanFinding] = {}
		sources: Dict[Tuple[str, str], List[str]] = {}
		for finding in findings:
			key = (finding.type.lower(), finding.file_path)
			sources.setdefault(key, [])
			sources[key].extend(list(finding.detection_source))
			existing = index.get(key)
			if not existing or finding.confidence > existing.confidence:
				index[key] = finding

		merged: List[ScanFinding] = []
		for key, finding in index.items():
			src_list = sorted(set(sources.get(key, [])))
			boost = min(0.1, max(0.0, 0.05 * (len(src_list) - 1)))
			finding.confidence = round(min(0.99, finding.confidence + boost), 2)
			finding.detection_source = src_list
			finding.code_snippet = self._best_snippet([finding.code_snippet, index[key].code_snippet])
			merged.append(finding)
		return merged

	def _best_snippet(self, snippets: List[str]) -> str:
		clean = [s.strip() for s in snippets if s and s.strip()]
		return max(clean, key=len) if clean else ""

	def _save_scan_output(self, output: dict) -> None:
		output_dir = Path("scans")
		output_dir.mkdir(parents=True, exist_ok=True)
		stamp = datetime.utcnow().strftime("%Y_%m_%d_%H%M%S")
		file_path = output_dir / f"scan_{stamp}.json"
		try:
			file_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
			self._logger.info("Scan output saved: %s", file_path)
		except OSError:
			self._logger.warning("Failed to write scan output: %s", file_path)

	def _as_dict(self, finding: ScanFinding) -> dict:
		return {
			"vulnerability_id": finding.vulnerability_id,
			"type": finding.type,
			"severity": finding.severity,
			"confidence": finding.confidence,
			"cwe_id": finding.cwe_id,
			"owasp_category": finding.owasp_category,
			"file_path": finding.file_path,
			"file_name": finding.file_name,
			"line_number": finding.line_number,
			"column_number": finding.column_number,
			"language": finding.language,
			"code_snippet": finding.code_snippet,
			"description": finding.description,
			"attack_surface": finding.attack_surface,
			"affected_component": finding.affected_component,
			"detection_source": finding.detection_source,
			"detected_at": finding.detected_at,
		}
