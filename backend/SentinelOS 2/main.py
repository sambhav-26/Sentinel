import os
from agents.scanner_agent import run_scan
from agents.attack_agent import analyze_attacks, load_scan_results, save_attack_results


def print_report(scan_results: dict, attack_results: dict) -> None:
    findings = scan_results.get("findings", [])
    analysis = attack_results.get("attack_analysis", [])

    print("=" * 50)
    print("        SENTINELOS SECURITY ANALYSIS")
    print("=" * 50)
    print(f"[+] Repository: {scan_results.get('repository', 'unknown')}")
    print("[+] Repository Scanned Successfully")
    print(f"[+] Vulnerabilities Detected: {len(findings)}")
    print("[+] Attack Simulation Completed")

    if not analysis:
        print("\nNo vulnerabilities detected. Analysis complete.")
        print("\n" + "=" * 50)
        print("        ANALYSIS COMPLETED")
        print("=" * 50)
        return

    for entry in analysis:
        print("\n" + "-" * 50)
        print(f"VULNERABILITY: {entry['vulnerability']}")
        print(f"FILE: {entry['file']} (Line {entry['line']})")
        print(f"SEVERITY: {entry['severity']}")
        print("EXPLANATION:")
        explanation = entry.get("human_readable_explanation", "")
        for line in (explanation.splitlines() or [""]):
            print(line)
        print(f"ATTACK TYPE: {entry['attack_type']}")
        print(f"SUCCESS PROBABILITY: {entry['success_probability']}")
        if entry.get("code_snippet"):
            print(f"CODE SNIPPET: {entry['code_snippet']}")
        print("\nPOSSIBLE ATTACK FLOW:")
        for idx, step in enumerate(entry["attack_path"], start=1):
            print(f"{idx}. {step}")
        print(f"\nIMPACT:\n{entry['impact']}")
        print(f"\nMITRE:\n{entry['mitre_technique']}")

    print("\n" + "=" * 50)
    print("        ANALYSIS COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    repo_path = input("Enter repository path: ").strip()
    if not repo_path:
        print("Repository path is required.")
        raise SystemExit(1)
    if not os.path.isdir(repo_path):
        print("Repository path does not exist or is not a folder.")
        raise SystemExit(1)

    scan_results = run_scan(repo_path)
    attack_results = analyze_attacks(load_scan_results())
    save_attack_results(attack_results)
    print_report(scan_results, attack_results)