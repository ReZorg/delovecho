---
name: pro-to-com-is-exe
description: Protocol-to-Command-is-Executable. An advanced legal case analysis skill using an integrated Promise-Lambda Attention (QKV) framework. Use for analyzing legal case repositories like revstream1 and ad-res-j7 to find evidence (K) that satisfies legal promises (Q) and generate enhanced legal filings (V).
---

# Protocol-to-Command-is-Executable (pro-to-com-is-exe)

This skill implements an advanced repository analysis workflow for legal cases based on the **Promise-Lambda Attention** paradigm (`λ(KV)^-1`). It integrates domain knowledge from `revstream-evidence` and `lex-case-analysis` into a unified QKV framework.

## The QKV Framework

| Component | Role | Source Skill & Implementation |
| :--- | :--- | :--- |
| **Q (λ.promise)** | **Legal Constraints** | `/promise-lambda-attention`: A `.promise` file defines the legal burden of proof, required evidence types, and statutory elements that must be satisfied. |
| **K (Protocol)** | **Evidence Structure** | `/revstream-evidence`: The repository's structure (`/docs`, `/evidence`), file formats, and metadata standards define the protocol for how evidence is organized. |
| **V (Execution)** | **Legal Analysis** | `/lex-case-analysis`: The generation of legal filings, evidence chain analysis, and entity-relation modeling are the concrete executions performed on the evidence. |

**Mechanism:** The core script, `legal_analyzer.py`, finds all evidence (`K`) and associated analyses (`V`) that satisfy the legal promise (`Q`).

## Workflow

1.  **Define the Promise (λ):** Create a `.promise` file at the repository root to define the legal constraints for the case.
2.  **Introspect the KV Space:** Analyze the repository's evidence structure (`revstream-evidence` protocol) to map the available Key-Value pairs.
3.  **Run the Legal Analyzer:** Execute `legal_analyzer.py` to find all `(KV)` pairs that satisfy the promise `λ`.
4.  **Generate Enhanced Filings:** Use the results to generate comprehensive, evidence-backed legal filings (`lex-case-analysis` execution).
5.  **Commit & Push:** Sync all changes to the repository.

## Phase 1: Define the Promise (λ)

Create a `.promise` file at the root of the target repository (e.g., `/home/ubuntu/revstream1/.promise`). Use the provided legal template.

```bash
# Copy the legal promise template to your repository root
cp /home/ubuntu/skills/pro-to-com-is-exe/templates/.promise.legal.template /path/to/your/repo/.promise
```

Edit the `.promise` file to specify the exact legal constraints for the case, such as:
- `burden_of_proof: criminal` (95% threshold)
- `required_evidence: ["financial_records", "communication_logs"]`
- `statutory_violations: ["CompaniesAct.s76", "POPIA.s107"]`

## Phase 2: Introspect the KV Space

Use standard introspection techniques to understand the repository's evidence structure (the `K` in our QKV model).

```bash
# In the target repository
ls -R docs/evidence/
ls -R ANNEXURES/
cat docs/evidence-index-enhanced.md
```

## Phase 3: Run the Legal Analyzer

Execute the `legal_analyzer.py` script, pointing it to the repository.

```bash
python /home/ubuntu/skills/pro-to-com-is-exe/scripts/legal_analyzer.py /path/to/your/repo
```

The script will:
1.  Read the `.promise` file.
2.  Traverse the repository to find all evidence files (the KV space).
3.  Report which files and evidence chains satisfy the promise.
4.  Output a `PROMISE_SATISFACTION_REPORT.md`.

## Phase 4: Generate Enhanced Filings

Based on the `PROMISE_SATISFACTION_REPORT.md`, use the `lex-case-analysis` skill to generate the final, enhanced legal filings. This is the "V" (Execution) in the QKV model.

## Bundled Resources

| Path | Description |
| :--- | :--- |
| `scripts/legal_analyzer.py` | The core analysis script that implements the `λ(KV)^-1` mechanism for legal cases. |
| `templates/.promise.legal.template` | A template for the `.promise` file, tailored for legal case analysis. |
| `references/QKV_Framework.md` | A detailed explanation of the integrated QKV framework. |
