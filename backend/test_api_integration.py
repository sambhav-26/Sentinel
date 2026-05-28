#!/usr/bin/env python3
"""
Integration test for API endpoints with agent orchestration.
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_scan_flow():
    """Test complete scan flow through API."""
    
    async with aiohttp.ClientSession() as session:
        print("\n" + "="*70)
        print("API INTEGRATION TEST")
        print("="*70)
        
        # Test 1: Create scan
        print("\n[1] Creating scan...")
        async with session.post(
            f"{BASE_URL}/api/scans",
            json={"repository_url": "https://github.com/test/security-audit"}
        ) as resp:
            if resp.status != 200:
                print(f"✗ Failed: {resp.status}")
                return False
            data = await resp.json()
            scan_id = data.get("id")
            print(f"✓ Scan created: {scan_id}")
            print(f"  Status: {data.get('status')}")
            print(f"  Progress: {data.get('progress')}%")
        
        # Test 2: List scans
        print("\n[2] Listing scans...")
        async with session.get(f"{BASE_URL}/api/scans") as resp:
            if resp.status != 200:
                print(f"✗ Failed: {resp.status}")
                return False
            data = await resp.json()
            items = data.get("items", [])
            print(f"✓ Found {len(items)} scans")
            if items:
                print(f"  Latest scan: {items[0].get('id')} - {items[0].get('status')}")
        
        # Test 3: Get scan details
        print("\n[3] Getting scan details...")
        await asyncio.sleep(1)  # Wait for background job
        async with session.get(f"{BASE_URL}/api/scans/{scan_id}") as resp:
            if resp.status != 200:
                print(f"✗ Failed: {resp.status}")
                return False
            data = await resp.json()
            print(f"✓ Scan details retrieved")
            print(f"  Status: {data.get('status')}")
            print(f"  Progress: {data.get('progress')}%")
            print(f"  Total Files: {data.get('total_files')}")
            print(f"  Files Scanned: {data.get('files_scanned')}")
            
            # Check if any findings
            findings = data.get('findings', {})
            total = findings.get('total', 0)
            critical = findings.get('critical', 0)
            high = findings.get('high', 0)
            medium = findings.get('medium', 0)
            low = findings.get('low', 0)
            
            if total > 0:
                print(f"  Findings: {total} total (Critical: {critical}, High: {high}, Medium: {medium}, Low: {low})")
        
        # Test 4: Get findings
        print("\n[4] Getting findings...")
        async with session.get(f"{BASE_URL}/api/scans/{scan_id}/findings") as resp:
            if resp.status != 200:
                print(f"✗ Failed: {resp.status}")
                return False
            data = await resp.json()
            items = data.get("items", [])
            print(f"✓ Retrieved {len(items)} findings")
            if items:
                finding = items[0]
                print(f"  Sample finding:")
                print(f"    Type: {finding.get('vulnerability_type')}")
                print(f"    Severity: {finding.get('severity')}")
                print(f"    File: {finding.get('file_path')}")
                print(f"    CWE: {finding.get('cwe_id')} - {finding.get('cwe_name')}")
        
        # Test 5: Get attacks
        print("\n[5] Getting attacks...")
        async with session.get(f"{BASE_URL}/api/scans/{scan_id}/attacks") as resp:
            if resp.status != 200:
                print(f"✗ Failed: {resp.status}")
                return False
            data = await resp.json()
            items = data.get("items", [])
            print(f"✓ Retrieved {len(items)} attacks")
            if items:
                attack = items[0]
                print(f"  Sample attack:")
                print(f"    Type: {attack.get('attack_type')}")
                print(f"    Success Rate: {attack.get('success_probability', 0)*100:.1f}%")
                print(f"    Impact: {attack.get('impact_score', 0)}/10")
                print(f"    MITRE: {attack.get('mitre_technique')}")
        
        # Test 6: Get patches
        print("\n[6] Getting patches...")
        async with session.get(f"{BASE_URL}/api/scans/{scan_id}/patches") as resp:
            if resp.status != 200:
                print(f"✗ Failed: {resp.status}")
                return False
            data = await resp.json()
            items = data.get("items", [])
            print(f"✓ Retrieved {len(items)} patches")
            if items:
                patch = items[0]
                print(f"  Sample patch:")
                print(f"    Confidence: {patch.get('confidence', 0)*100:.1f}%")
                print(f"    Complexity: {patch.get('apply_complexity')}")
                print(f"    Auto-apply: {'Yes' if patch.get('can_auto_apply') else 'No'}")
        
        # Test 7: Get report
        print("\n[7] Getting report...")
        async with session.get(f"{BASE_URL}/api/scans/{scan_id}/report") as resp:
            if resp.status != 200:
                print(f"✗ Failed: {resp.status}")
                return False
            data = await resp.json()
            print(f"✓ Report retrieved")
            print(f"  Risk Score: {data.get('overall_risk_score', 0):.0f}/100")
            print(f"  Patch Coverage: {data.get('patch_coverage', 0):.1f}%")
            print(f"  Est. Remediation: {data.get('estimated_remediation_time', 0):.1f}h")
            
            summary = data.get('executive_summary', '')
            if summary:
                lines = summary.split('\n')[:3]
                print(f"  Summary: {lines[0][:60]}...")
        
        # Summary
        print("\n" + "="*70)
        print("✓ ALL API TESTS PASSED!")
        print("="*70)
        return True


async def main():
    try:
        success = await test_scan_flow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
