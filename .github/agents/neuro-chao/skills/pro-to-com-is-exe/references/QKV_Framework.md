# QKV Framework for Legal Case Analysis

## Overview

The **Protocol-to-Command-is-Executable** (pro-to-com-is-exe) skill implements a specialized version of the Promise-Lambda Attention paradigm, adapted for legal case analysis. This document explains the theoretical foundation and practical application of the QKV framework.

## The Promise-Lambda Attention Paradigm

Traditional attention mechanisms ask: "What am I looking for?" and retrieve relevant information. The Promise-Lambda Attention paradigm inverts this: a **promise (λ)** asserts constraints, and the system finds all **protocol-execution (KV)** pairs that satisfy it.

### Mathematical Foundation

```
λ(KV)^-1
```

This notation means: find all (KV) pairs whose generative history satisfies the promise λ.

## QKV Mapping for Legal Cases

| Component | Standard Attention | Promise-Lambda | Legal Application |
| :--- | :--- | :--- | :--- |
| **Q** | "What am I looking for?" | **λ.promise**: "What *must* be true." | Legal constraints: burden of proof, required evidence, statutory violations |
| **K** | "What information is available?" | **Protocol**: An interpretive framework. | Evidence structure: file formats, metadata, repository organization |
| **V** | "What information do I get?" | **Execution**: A concrete action. | Legal outputs: filings, entity models, evidence chains |

## Source Skill Integration

### Q: `/promise-lambda-attention`

The Query component defines the legal constraints that must be satisfied. In the `.promise` file, we specify:

- **Burden of Proof**: Civil (50%) or Criminal (95%)
- **Required Evidence Types**: Financial records, communications, corporate records
- **Statutory Violations**: CompaniesAct.s76, POPIA.s107, TaxAdmin.s234

### K: `/revstream-evidence`

The Key component defines the protocol for how evidence is organized:

- **Repository Structure**: `/docs`, `/evidence`, `/ANNEXURES`
- **File Formats**: Markdown, JSON, PDF, images
- **Metadata Standards**: Evidence codes (JF01, SF1), dates, entities

### V: `/lex-case-analysis`

The Value component defines the concrete executions:

- **Legal Filings**: CIPC complaints, POPIA complaints, NPA reports
- **Entity-Relation Models**: Mapping perpetrators, victims, entities
- **Evidence Chains**: Linking evidence to legal elements

## Workflow Implementation

### Step 1: Define λ (The Promise)

Create a `.promise` file that specifies the legal constraints:

```yaml
burden_of_proof: criminal
required_evidence:
  - financial_records
  - communication_logs
statutory_violations:
  - CompaniesAct.s76
  - POPIA.s107
```

### Step 2: Discover KV Space

The `legal_analyzer.py` script traverses the repository to find all evidence files and classifies them by type and category.

### Step 3: Apply λ(KV)^-1

For each evidence file (KV pair), the analyzer checks if it satisfies the promise constraints. Files that match required evidence types or support statutory violations are marked as satisfying the promise.

### Step 4: Generate V (Execution)

The `PROMISE_SATISFACTION_REPORT.md` identifies which evidence supports which legal claims, enabling the generation of targeted legal filings.

## Burden of Proof Thresholds

| Standard | Threshold | Application |
|----------|-----------|-------------|
| Civil | 50% | Balance of probabilities |
| Criminal | 95% | Beyond reasonable doubt |

The analyzer calculates a satisfaction score for each evidence file. Files with scores above the threshold are considered to satisfy the promise.

## Example Application: Case 2025-137857

### Promise (λ)

```yaml
burden_of_proof: criminal
required_evidence:
  - financial_records
  - revenue_records
statutory_violations:
  - CompaniesAct.s162
  - POPIA.s107
```

### Evidence (K)

- Bank statements (Oct 2024, Mar 2025)
- Shopify sales reports
- CIPC company records
- Email correspondence

### Execution (V)

- CIPC Director Disqualification Complaint
- POPIA Criminal Complaint
- NPA Tax Fraud Report
- Commercial Crime Submission

## Conclusion

The QKV framework transforms legal case analysis from a manual, ad-hoc process into a systematic, constraint-driven workflow. By defining the promise (λ) upfront, we ensure that all evidence is evaluated against consistent legal standards, and that the resulting filings are comprehensive and evidence-backed.
