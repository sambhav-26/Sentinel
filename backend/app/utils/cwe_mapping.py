"""CWE (Common Weakness Enumeration) mapping definitions."""

CWE_MAPPING = {
    "SQL Injection": ("CWE-89", "A03:2021 Injection"),
    "NoSQL Injection": ("CWE-943", "A03:2021 Injection"),
    "Command Injection": ("CWE-78", "A03:2021 Injection"),
    "OS Command Injection": ("CWE-78", "A03:2021 Injection"),
    "Dangerous Code Execution": ("CWE-94", "A03:2021 Injection"),
    "Dangerous eval() usage": ("CWE-94", "A03:2021 Injection"),
    "Unsafe subprocess usage": ("CWE-78", "A03:2021 Injection"),
    
    "Hardcoded Password": ("CWE-259", "A07:2021 Identification and Authentication Failures"),
    "Hardcoded Secret": ("CWE-798", "A07:2021 Identification and Authentication Failures"),
    "Hardcoded API Key": ("CWE-798", "A07:2021 Identification and Authentication Failures"),
    "Weak JWT Secret": ("CWE-798", "A07:2021 Identification and Authentication Failures"),
    
    "Debug Mode Enabled": ("CWE-489", "A05:2021 Security Misconfiguration"),
    "Insecure Assertion Usage": ("CWE-617", "A05:2021 Security Misconfiguration"),
    "Privileged Container": ("CWE-250", "A05:2021 Security Misconfiguration"),
    "Host Network Exposure": ("CWE-284", "A05:2021 Security Misconfiguration"),
    
    "XSS": ("CWE-79", "A03:2021 Injection"),
    "Cross-Site Scripting": ("CWE-79", "A03:2021 Injection"),
    
    "Weak Cryptography": ("CWE-327", "A02:2021 Cryptographic Failures"),
    "MD5 Usage": ("CWE-327", "A02:2021 Cryptographic Failures"),
    "SHA1 Usage": ("CWE-327", "A02:2021 Cryptographic Failures"),
    
    "Unpinned Dependency": ("CWE-1104", "A06:2021 Vulnerable and Outdated Components"),
    "Vulnerable Dependency": ("CWE-1035", "A06:2021 Vulnerable and Outdated Components"),
}


def get_cwe_mapping(vulnerability_type: str) -> tuple[str, str]:
    """
    Get CWE ID and OWASP category for vulnerability type.
    
    Args:
        vulnerability_type: Vulnerability name
        
    Returns:
        Tuple of (CWE_ID, OWASP_CATEGORY)
    """
    return CWE_MAPPING.get(vulnerability_type, ("CWE-Unknown", "Unknown"))
