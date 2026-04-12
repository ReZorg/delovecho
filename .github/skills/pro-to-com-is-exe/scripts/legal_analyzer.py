#!/usr/bin/env python3
"""
Legal Analyzer: λ(KV)^-1 Implementation for Legal Case Analysis

This script implements the Promise-Lambda Attention paradigm for legal cases.
It finds all evidence (K) and associated analyses (V) that satisfy the legal promise (Q).

Usage:
    python legal_analyzer.py /path/to/repository
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime


def load_promise(repo_path: str) -> dict:
    """Load the .promise file from the repository root."""
    promise_path = Path(repo_path) / ".promise"
    if not promise_path.exists():
        print(f"Error: No .promise file found at {promise_path}")
        print("Create one using: cp /home/ubuntu/skills/pro-to-com-is-exe/templates/.promise.legal.template .promise")
        sys.exit(1)
    
    with open(promise_path, 'r') as f:
        return yaml.safe_load(f)


def discover_evidence(repo_path: str) -> list:
    """Discover all evidence files in the repository (the KV space)."""
    evidence_files = []
    evidence_dirs = ['docs', 'evidence', 'ANNEXURES', 'evidence_documents', 'data_models']
    evidence_extensions = ['.md', '.json', '.pdf', '.png', '.jpg', '.txt', '.csv']
    
    for evidence_dir in evidence_dirs:
        dir_path = Path(repo_path) / evidence_dir
        if dir_path.exists():
            for ext in evidence_extensions:
                evidence_files.extend(dir_path.rglob(f"*{ext}"))
    
    return evidence_files


def classify_evidence(file_path: Path) -> dict:
    """Classify an evidence file based on its name and location."""
    name = file_path.name.lower()
    path_str = str(file_path).lower()
    
    classification = {
        "path": str(file_path),
        "name": file_path.name,
        "type": "unknown",
        "categories": []
    }
    
    # Classify by type
    if any(x in name for x in ['bank', 'statement', 'fnb', 'absa']):
        classification["type"] = "financial_records"
        classification["categories"].append("banking")
    elif any(x in name for x in ['email', 'mail', 'correspondence']):
        classification["type"] = "communication_logs"
        classification["categories"].append("communications")
    elif any(x in name for x in ['cipc', 'company', 'director']):
        classification["type"] = "corporate_records"
        classification["categories"].append("companies_act")
    elif any(x in name for x in ['popia', 'data', 'privacy']):
        classification["type"] = "data_protection"
        classification["categories"].append("popia")
    elif any(x in name for x in ['tax', 'sars', 'vat']):
        classification["type"] = "tax_records"
        classification["categories"].append("tax_fraud")
    elif any(x in name for x in ['shopify', 'sales', 'revenue']):
        classification["type"] = "revenue_records"
        classification["categories"].append("revenue_hijacking")
    elif any(x in name for x in ['timeline', 'event']):
        classification["type"] = "timeline"
        classification["categories"].append("forensic")
    elif any(x in name for x in ['entity', 'relation']):
        classification["type"] = "entity_model"
        classification["categories"].append("entity_relation")
    
    return classification


def check_promise_satisfaction(evidence: dict, promise: dict) -> dict:
    """Check if an evidence file satisfies the promise constraints."""
    result = {
        "satisfies": False,
        "matches": [],
        "score": 0.0
    }
    
    # Check required evidence types
    required_evidence = promise.get("required_evidence", [])
    for req in required_evidence:
        if evidence["type"] == req or req in evidence["categories"]:
            result["matches"].append(f"required_evidence:{req}")
            result["score"] += 0.3
    
    # Check statutory violations
    statutory_violations = promise.get("statutory_violations", [])
    for violation in statutory_violations:
        if any(v.lower() in str(evidence["categories"]).lower() for v in [violation.split('.')[0]]):
            result["matches"].append(f"statutory_violation:{violation}")
            result["score"] += 0.2
    
    # Determine if promise is satisfied based on burden of proof
    burden = promise.get("burden_of_proof", "civil")
    threshold = 0.5 if burden == "civil" else 0.95
    
    if result["score"] > 0:
        result["satisfies"] = True
    
    return result


def generate_report(repo_path: str, promise: dict, results: list) -> str:
    """Generate the PROMISE_SATISFACTION_REPORT.md."""
    report_path = Path(repo_path) / "PROMISE_SATISFACTION_REPORT.md"
    
    satisfied = [r for r in results if r["satisfaction"]["satisfies"]]
    
    report = f"""# Promise Satisfaction Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Repository:** {repo_path}  
**Burden of Proof:** {promise.get("burden_of_proof", "civil")}

## Promise (λ)

```yaml
{yaml.dump(promise, default_flow_style=False)}
```

## Summary

| Metric | Value |
|--------|-------|
| Total Evidence Files | {len(results)} |
| Files Satisfying Promise | {len(satisfied)} |
| Satisfaction Rate | {len(satisfied)/len(results)*100:.1f}% |

## Evidence Satisfying Promise (KV Pairs)

| File | Type | Categories | Score | Matches |
|------|------|------------|-------|---------|
"""
    
    for r in sorted(satisfied, key=lambda x: x["satisfaction"]["score"], reverse=True):
        matches = ", ".join(r["satisfaction"]["matches"][:3])
        report += f"| {r['evidence']['name'][:40]} | {r['evidence']['type']} | {', '.join(r['evidence']['categories'][:2])} | {r['satisfaction']['score']:.2f} | {matches} |\n"
    
    report += """

## Recommended Actions

Based on the evidence satisfying the promise, the following legal filings can be generated:

1. **CIPC Complaint** - If corporate_records evidence found
2. **POPIA Complaint** - If data_protection evidence found
3. **NPA Tax Fraud Report** - If tax_records evidence found
4. **Commercial Crime Submission** - If financial_records evidence found

Use the `/lex-case-analysis` skill to generate these filings.
"""
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    return str(report_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python legal_analyzer.py /path/to/repository")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    if not Path(repo_path).exists():
        print(f"Error: Repository path does not exist: {repo_path}")
        sys.exit(1)
    
    print(f"🔍 Legal Analyzer: λ(KV)^-1")
    print(f"   Repository: {repo_path}")
    print()
    
    # Load the promise (Q)
    print("📜 Loading Promise (λ)...")
    promise = load_promise(repo_path)
    print(f"   Burden of Proof: {promise.get('burden_of_proof', 'civil')}")
    print(f"   Required Evidence: {promise.get('required_evidence', [])}")
    print()
    
    # Discover evidence (K)
    print("🔎 Discovering Evidence (K)...")
    evidence_files = discover_evidence(repo_path)
    print(f"   Found {len(evidence_files)} evidence files")
    print()
    
    # Analyze each evidence file
    print("⚖️ Checking Promise Satisfaction...")
    results = []
    for file_path in evidence_files:
        evidence = classify_evidence(file_path)
        satisfaction = check_promise_satisfaction(evidence, promise)
        results.append({
            "evidence": evidence,
            "satisfaction": satisfaction
        })
    
    satisfied = [r for r in results if r["satisfaction"]["satisfies"]]
    print(f"   {len(satisfied)}/{len(results)} files satisfy the promise")
    print()
    
    # Generate report (V)
    print("📝 Generating Report (V)...")
    report_path = generate_report(repo_path, promise, results)
    print(f"   Report saved to: {report_path}")
    print()
    
    print("✅ Analysis complete!")


if __name__ == "__main__":
    main()
