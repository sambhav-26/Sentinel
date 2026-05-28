"""MITRE ATT&CK framework mapping definitions."""

MITRE_TECHNIQUES = {
    # Execution
    "T1059": ("Command and Scripting Interpreter", "Execution"),
    "T1203": ("Exploitation for Client Execution", "Execution"),
    
    # Persistence
    "T1098": ("Account Manipulation", "Persistence"),
    "T1547": ("Boot or Logon Autostart Execution", "Persistence"),
    
    # Privilege Escalation
    "T1548": ("Abuse Elevation Control Mechanism", "Privilege Escalation"),
    "T1134": ("Access Token Manipulation", "Privilege Escalation"),
    
    # Defense Evasion
    "T1197": ("BITS Jobs", "Defense Evasion"),
    "T1027": ("Obfuscated Files or Information", "Defense Evasion"),
    
    # Credential Access
    "T1110": ("Brute Force", "Credential Access"),
    "T1555": ("Credentials from Password Stores", "Credential Access"),
    "T1552": ("Unsecured Credentials", "Credential Access"),
    
    # Discovery
    "T1087": ("Account Discovery", "Discovery"),
    "T1580": ("Cloud Infrastructure Discovery", "Discovery"),
    
    # Collection
    "T1557": ("Adversary-in-the-Middle", "Collection"),
    "T1123": ("Audio Capture", "Collection"),
    
    # Exfiltration
    "T1020": ("Automated Exfiltration", "Exfiltration"),
    "T1048": ("Exfiltration Over Alternative Protocol", "Exfiltration"),
    
    # Command & Control
    "T1071": ("Application Layer Protocol", "Command and Control"),
    "T1092": ("Communication Through Removable Media", "Command and Control"),
    
    # Impact
    "T1531": ("Account Access Removal", "Impact"),
    "T1485": ("Data Destruction", "Impact"),
    "T1561": ("Disk Wipe", "Impact"),
    
    # Initial Access
    "T1189": ("Drive-by Compromise", "Initial Access"),
    "T1190": ("Exploit Public-Facing Application", "Initial Access"),
    "T1199": ("Trusted Relationship", "Initial Access"),
    "T1566": ("Phishing", "Initial Access"),
    "T1091": ("Replication Through Removable Media", "Initial Access"),
}


def get_mitre_technique(technique_id: str) -> tuple[str, str]:
    """
    Get MITRE ATT&CK technique name and tactic.
    
    Args:
        technique_id: MITRE technique ID (e.g., "T1059")
        
    Returns:
        Tuple of (technique_name, tactic)
    """
    return MITRE_TECHNIQUES.get(technique_id, ("Unknown Technique", "Unknown"))
