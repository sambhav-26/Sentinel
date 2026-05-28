CWE_MAPPING = {
	"SQL Injection": ("CWE-89", "A03:2021 Injection"),
	"NoSQL Injection": ("CWE-943", "A03:2021 Injection"),
	"Command Injection": ("CWE-78", "A03:2021 Injection"),
	"Dangerous Code Execution": ("CWE-94", "A03:2021 Injection"),
	"Hardcoded Password": ("CWE-259", "A07:2021 Identification and Authentication Failures"),
	"Weak JWT Secret": ("CWE-798", "A07:2021 Identification and Authentication Failures"),
	"Hardcoded Secret": ("CWE-798", "A07:2021 Identification and Authentication Failures"),
	"Debug Mode Enabled": ("CWE-489", "A05:2021 Security Misconfiguration"),
	"XSS": ("CWE-79", "A03:2021 Injection"),
	"Weak Cryptography": ("CWE-327", "A02:2021 Cryptographic Failures"),
	"Insecure Assertion Usage": ("CWE-617", "A05:2021 Security Misconfiguration"),
	"Privileged Container": ("CWE-250", "A05:2021 Security Misconfiguration"),
	"Host Network Exposure": ("CWE-284", "A05:2021 Security Misconfiguration"),
	"Unpinned Dependency": ("CWE-1104", "A06:2021 Vulnerable and Outdated Components"),
}


def get_cwe_mapping(finding_type: str) -> tuple[str, str]:
	"""Return CWE and OWASP mapping for a finding type."""
	return CWE_MAPPING.get(finding_type, ("Unknown", "Unknown"))
