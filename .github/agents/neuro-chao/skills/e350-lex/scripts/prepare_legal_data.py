#!/usr/bin/env python3
"""
prepare_legal_data.py — Convert LEX legal framework into training data for Erebus 350M.

Extracts instruction-response pairs from:
  - lex-case-analysis: Entity-relation definitions, legal domain skills
  - super-sleuth: Evidence patterns, forensic analysis templates
  - hyper-holmes: Burden of proof, legal filing templates
  - provable-foreknowledge: Temporal audit trail generation

Outputs JSONL files suitable for HuggingFace Trainer or KoboldAI fine-tuning.

Usage:
    python prepare_legal_data.py --repo-dir ./ad-res-j7 --output-dir ./training_data
    python prepare_legal_data.py --skills-dir /home/ubuntu/skills --output-dir ./training_data
    python prepare_legal_data.py --all --output-dir ./training_data
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ── Training Sample Types ──


@dataclass
class TrainingSample:
    """A single instruction-response training pair."""
    task: str           # Task category
    instruction: str    # Input prompt
    response: str       # Expected output
    source: str         # Source skill/file
    genre_tag: str = "legal"  # Erebus genre tag

    def to_erebus_format(self) -> str:
        """Format as Erebus-style tagged prompt + completion."""
        return (
            f"[Genre: {self.genre_tag}]\n"
            f"[Task: {self.task}]\n"
            f"{self.instruction}\n"
            f"---\n"
            f"{self.response}"
        )

    def to_instruction_format(self) -> dict:
        """Format as instruction-response JSON for SFT."""
        return {
            "instruction": self.instruction,
            "response": self.response,
            "task": self.task,
            "source": self.source,
            "genre_tag": self.genre_tag,
        }

    def to_chat_format(self) -> dict:
        """Format as chat messages for OpenAI-compatible training."""
        return {
            "messages": [
                {"role": "system", "content": f"You are a legal analysis AI specializing in {self.task}. Use the LEX Legal Reasoning Framework."},
                {"role": "user", "content": self.instruction},
                {"role": "assistant", "content": self.response},
            ]
        }


# ── Data Extractors ──


def extract_entity_relation_samples(repo_dir: Path) -> list[TrainingSample]:
    """Extract entity-relation training samples from LEX core files."""
    samples = []
    core_dir = repo_dir / "lex" / "core"

    if not core_dir.exists():
        print(f"  [WARN] LEX core directory not found: {core_dir}")
        return samples

    # Entity types and their analysis patterns
    entity_types = {
        "natural-person": "Analyze this natural person's roles, affiliations, and legal exposure.",
        "juristic-person": "Analyze this company's directors, shareholders, compliance status, and legal obligations.",
        "trust": "Analyze this trust's trustees, beneficiaries, assets, and fiduciary duties.",
        "account": "Analyze this financial account's holder, transactions, and suspicious patterns.",
    }

    for etype, prompt_template in entity_types.items():
        samples.append(TrainingSample(
            task="entity_analysis",
            instruction=f"[Entity Type: {etype}]\n{prompt_template}",
            response=(
                f"## Entity Analysis: {etype.replace('-', ' ').title()}\n\n"
                f"### Identification\n"
                f"- Type: {etype}\n"
                f"- Classification: [primary/secondary/peripheral]\n\n"
                f"### Relations\n"
                f"- [relation_type]: [target_entity] (confidence: [0.0-1.0])\n\n"
                f"### Legal Exposure\n"
                f"- [legal_element]: [evidence_weight] (threshold: [civil/criminal])\n\n"
                f"### Risk Assessment\n"
                f"- Overall risk: [low/medium/high/critical]\n"
                f"- Key factors: [list factors]\n"
            ),
            source="lex-case-analysis/entity-relation",
            genre_tag="legal analysis",
        ))

    # Relation types
    relations = [
        ("director_of", "NP → JP", "Analyze the director's duties under Companies Act s76-77."),
        ("shareholder_of", "NP/JP/TR → JP", "Analyze the shareholder's rights and voting power."),
        ("trustee_of", "NP → TR", "Analyze the trustee's fiduciary duties under the Trust Property Control Act."),
        ("beneficiary_of", "NP → TR", "Analyze the beneficiary's rights and entitlements."),
        ("controls", "NP → AC", "Analyze the account controller's authority and transaction patterns."),
        ("transferred_to", "AC → AC", "Trace the fund flow and assess for suspicious patterns."),
    ]

    for rel_type, direction, prompt in relations:
        samples.append(TrainingSample(
            task="relation_analysis",
            instruction=f"[Relation: {rel_type} ({direction})]\n{prompt}",
            response=(
                f"## Relation Analysis: {rel_type}\n\n"
                f"### Direction: {direction}\n\n"
                f"### Legal Framework\n"
                f"- Applicable legislation: [Act and section]\n"
                f"- Duty/obligation: [description]\n\n"
                f"### Evidence Assessment\n"
                f"- Source documents: [list]\n"
                f"- Confidence: [0.0-1.0]\n"
                f"- Corroboration: [independent sources]\n\n"
                f"### Breach Analysis\n"
                f"- Duty breached: [yes/no]\n"
                f"- Elements met: [list elements]\n"
                f"- Evidence weight: [calculated weight]\n"
            ),
            source="lex-case-analysis/relations",
            genre_tag="legal analysis",
        ))

    # Scan for .scm files with entity definitions
    for scm_file in core_dir.glob("*.scm"):
        try:
            content = scm_file.read_text(encoding="utf-8", errors="replace")
            # Extract entity definitions
            entity_defs = re.findall(
                r'\(define\s+\w+\s+\(make-entity\s+"([^"]+)"\s+\'(\S+)\s+"([^"]+)"',
                content
            )
            for entity_id, entity_type, entity_name in entity_defs:
                samples.append(TrainingSample(
                    task="entity_description",
                    instruction=f"Describe the entity: {entity_name} (ID: {entity_id}, Type: {entity_type})",
                    response=(
                        f"## Entity: {entity_name}\n\n"
                        f"- **ID**: {entity_id}\n"
                        f"- **Type**: {entity_type}\n"
                        f"- **Role**: [Determined from case context]\n"
                        f"- **Relations**: [Mapped from entity-relation model]\n"
                        f"- **Legal exposure**: [Assessed from evidence chains]\n"
                    ),
                    source=f"lex-case-analysis/{scm_file.name}",
                    genre_tag="legal analysis",
                ))
        except Exception as e:
            print(f"  [WARN] Error reading {scm_file}: {e}")

    print(f"  Extracted {len(samples)} entity-relation samples")
    return samples


def extract_evidence_chain_samples(skills_dir: Path) -> list[TrainingSample]:
    """Extract evidence chain building samples from super-sleuth patterns."""
    samples = []

    # Forensic patterns from super-sleuth
    forensic_patterns = [
        ("manufactured_crisis", "Manufactured Crisis",
         "Detect manufactured crisis patterns: artificial urgency, deadline pressure, coordinated timing.",
         "Indicators: sudden deadlines, simultaneous multi-party actions, pressure to sign without review.\n"
         "Legal relevance: duress defense, undue influence, voidable contracts.\n"
         "Evidence to seek: communication records showing coordination, timeline showing artificial urgency."),
        ("revenue_hijacking", "Revenue Hijacking",
         "Detect revenue hijacking patterns: diverted payments, altered bank details, unauthorized account changes.",
         "Indicators: changed payment instructions, new intermediary accounts, discrepancies between invoiced and received amounts.\n"
         "Legal relevance: fraud, theft, breach of fiduciary duty.\n"
         "Evidence to seek: bank statements, payment instructions, account change authorizations."),
        ("identity_substitution", "Identity Substitution",
         "Detect identity substitution patterns: unauthorized signatories, forged documents, impersonation.",
         "Indicators: signature discrepancies, unauthorized CIPC changes, documents signed by non-authorized persons.\n"
         "Legal relevance: forgery, fraud, Companies Act violations.\n"
         "Evidence to seek: signature comparisons, CIPC records, authorization documents."),
        ("asset_stripping", "Asset Stripping",
         "Detect asset stripping patterns: rapid transfers before litigation, undervalued sales, hidden assets.",
         "Indicators: large transfers to related parties, sales below market value, timing relative to legal proceedings.\n"
         "Legal relevance: fraudulent conveyance, breach of fiduciary duty, contempt of court.\n"
         "Evidence to seek: transfer records, valuations, timing analysis."),
        ("coordinated_action", "Coordinated Action",
         "Detect coordinated action patterns: synchronized multi-party moves, communication clustering, parallel actions.",
         "Indicators: events within 7-day windows, communication bursts, parallel filings or transfers.\n"
         "Legal relevance: conspiracy, common purpose doctrine, joint and several liability.\n"
         "Evidence to seek: communication logs, event timeline, transaction records."),
    ]

    for pattern_id, pattern_name, instruction, response in forensic_patterns:
        samples.append(TrainingSample(
            task="pattern_detection",
            instruction=f"[Pattern: {pattern_name}]\n{instruction}",
            response=f"## Forensic Pattern: {pattern_name}\n\n{response}",
            source="super-sleuth/forensic_patterns",
            genre_tag="forensic analysis",
        ))

    # Evidence classification
    evidence_types = [
        ("primary", "High", "Bank statements, contracts, certificates, CIPC records"),
        ("secondary", "Medium", "Emails, messages, meeting notes, correspondence"),
        ("tertiary", "Low", "Hearsay, unverified claims, social media posts"),
    ]

    for etype, reliability, examples in evidence_types:
        samples.append(TrainingSample(
            task="evidence_classification",
            instruction=f"Classify and assess this evidence type: {etype} (reliability: {reliability})",
            response=(
                f"## Evidence Classification: {etype.title()}\n\n"
                f"- **Reliability**: {reliability}\n"
                f"- **Examples**: {examples}\n"
                f"- **Admissibility**: [Assess under Law of Evidence Amendment Act 45 of 1988]\n"
                f"- **Weight**: [Calculate based on source authenticity, directness, corroboration]\n"
                f"- **Chain of custody**: [Verify provenance and integrity]\n"
            ),
            source="super-sleuth/evidence_classification",
            genre_tag="forensic analysis",
        ))

    # Timeline reconstruction
    samples.append(TrainingSample(
        task="timeline_reconstruction",
        instruction=(
            "Reconstruct a forensic timeline from the following events. "
            "Identify gaps, clusters, and anomalies. Calculate T-reference "
            "months relative to the key future event."
        ),
        response=(
            "## Forensic Timeline Reconstruction\n\n"
            "### Methodology\n"
            "1. Extract all timestamps from verified facts\n"
            "2. Sort chronologically\n"
            "3. Identify gaps (missing periods > 30 days)\n"
            "4. Detect clusters (3+ events within 7-day windows)\n"
            "5. Calculate T-reference (months to key event)\n"
            "6. Flag anomalies (out-of-sequence, backdated)\n\n"
            "### Timeline\n"
            "| Date | Event | T-Ref | Source | Anomaly |\n"
            "|------|-------|-------|--------|---------|\n"
            "| [date] | [event] | T-[N] | [source] | [flag] |\n\n"
            "### Clusters Detected\n"
            "- [dates]: [events] — Significance: [coordination/escalation/concealment]\n\n"
            "### Gaps Identified\n"
            "- [period]: Missing records — Significance: [concealment/destruction/negligence]\n"
        ),
        source="super-sleuth/timeline",
        genre_tag="forensic analysis",
    ))

    # Fund flow tracing
    suspicious_patterns = [
        ("structuring", "Multiple transactions just below reporting threshold"),
        ("layering", "Rapid transfers through multiple accounts"),
        ("round_tripping", "Funds return to origin via intermediaries"),
        ("smurfing", "Multiple small deposits from different sources"),
        ("integration", "Large purchases after layering phase"),
    ]

    for pattern, description in suspicious_patterns:
        samples.append(TrainingSample(
            task="fund_flow_analysis",
            instruction=f"Analyze fund flow for {pattern} pattern: {description}",
            response=(
                f"## Fund Flow Analysis: {pattern.replace('_', ' ').title()}\n\n"
                f"### Pattern Definition\n{description}\n\n"
                f"### Detection Criteria\n"
                f"- Transaction threshold: [amount]\n"
                f"- Time window: [period]\n"
                f"- Account count: [minimum]\n\n"
                f"### Red Flag Level: [High/Critical]\n\n"
                f"### Legal Framework\n"
                f"- Prevention of Organised Crime Act 121 of 1998 (POCA)\n"
                f"- Financial Intelligence Centre Act 38 of 2001 (FICA)\n"
                f"- Section: [relevant section]\n\n"
                f"### Required Evidence\n"
                f"- Bank statements showing pattern\n"
                f"- Account holder identification\n"
                f"- Transaction timing analysis\n"
            ),
            source="super-sleuth/fund_flow",
            genre_tag="forensic analysis",
        ))

    print(f"  Extracted {len(samples)} evidence chain samples")
    return samples


def extract_burden_of_proof_samples(skills_dir: Path) -> list[TrainingSample]:
    """Extract burden of proof assessment samples from hyper-holmes."""
    samples = []

    # Legal elements with thresholds
    legal_elements = [
        ("fraud", "civil", 0.50, ["misrepresentation", "intent", "reliance", "damage"]),
        ("fraud", "criminal", 0.95, ["misrepresentation", "intent", "reliance", "damage", "unlawfulness"]),
        ("breach_of_fiduciary_duty", "civil", 0.50, ["duty", "breach", "causation", "damage"]),
        ("money_laundering", "criminal", 0.95, ["predicate_offense", "concealment", "knowledge"]),
        ("forgery", "criminal", 0.95, ["false_document", "intent_to_defraud"]),
        ("tax_fraud", "criminal", 0.95, ["false_return", "intent", "material_amount"]),
        ("popia_breach", "civil", 0.50, ["personal_information", "processing", "no_consent", "harm"]),
        ("companies_act_violation", "civil", 0.50, ["duty_under_act", "breach", "prejudice"]),
    ]

    for element, standard, threshold, required in legal_elements:
        element_name = element.replace("_", " ").title()
        samples.append(TrainingSample(
            task="burden_assessment",
            instruction=(
                f"Assess burden of proof for: {element_name}\n"
                f"Standard: {standard} ({threshold*100:.0f}%)\n"
                f"Required elements: {', '.join(required)}"
            ),
            response=(
                f"## Burden of Proof Assessment: {element_name}\n\n"
                f"### Standard: {standard.title()} ({threshold*100:.0f}%)\n\n"
                f"### Element Analysis\n\n" +
                "\n".join([
                    f"#### {elem.replace('_', ' ').title()}\n"
                    f"- Evidence: [list supporting evidence]\n"
                    f"- Weight: [calculated weight 0.0-1.0]\n"
                    f"- Met: [yes/no]\n"
                    for elem in required
                ]) +
                f"\n### Overall Assessment\n"
                f"- Combined score: [weighted sum]\n"
                f"- Threshold: {threshold}\n"
                f"- Status: [THRESHOLD_EXCEEDED / THRESHOLD_NOT_MET]\n"
                f"- Ready for filing: [yes/no]\n"
            ),
            source="hyper-holmes/burden_assessment",
            genre_tag="legal reasoning",
        ))

    # Evidence weighting
    reliability_levels = [
        ("conclusive", 1.0, "Signed contracts, bank records, official registers"),
        ("strong", 0.8, "Official documents, certified copies, audited statements"),
        ("moderate", 0.6, "Emails, correspondence, meeting minutes"),
        ("weak", 0.4, "Witness statements, hearsay, informal notes"),
        ("speculative", 0.2, "Inferences, patterns, circumstantial indicators"),
    ]

    for level, score, examples in reliability_levels:
        samples.append(TrainingSample(
            task="evidence_weighting",
            instruction=f"Calculate evidence weight for {level} reliability evidence: {examples}",
            response=(
                f"## Evidence Weight: {level.title()} (Base Score: {score})\n\n"
                f"### Calculation\n"
                f"```\n"
                f"Element_Weight = Evidence_Weight x Relevance x Reliability\n"
                f"             = [weight] x [relevance 0-1] x {score}\n"
                f"```\n\n"
                f"### Validation Criteria\n"
                f"| Criterion | Weight | Assessment |\n"
                f"|-----------|--------|------------|\n"
                f"| Source Authenticity | 0.30 | [score] |\n"
                f"| Direct Evidence | 0.25 | [score] |\n"
                f"| Corroboration | 0.20 | [score] |\n"
                f"| No Contradiction | 0.15 | [score] |\n"
                f"| Chain of Custody | 0.10 | [score] |\n\n"
                f"### Examples: {examples}\n"
            ),
            source="hyper-holmes/evidence_weighting",
            genre_tag="legal reasoning",
        ))

    print(f"  Extracted {len(samples)} burden of proof samples")
    return samples


def extract_foreknowledge_samples(skills_dir: Path) -> list[TrainingSample]:
    """Extract foreknowledge audit trail samples from provable-foreknowledge."""
    samples = []

    # Agent classification tiers
    tiers = [
        ("A", "Direct admission or documentary proof of knowledge before the act"),
        ("B", "Strong circumstantial evidence of knowledge (cc'd on emails, present at meetings)"),
        ("C", "Constructive knowledge (should have known based on role/duty)"),
        ("D", "Insufficient evidence of foreknowledge"),
    ]

    for tier, description in tiers:
        samples.append(TrainingSample(
            task="foreknowledge_classification",
            instruction=f"Classify agent foreknowledge as Tier {tier}: {description}",
            response=(
                f"## Foreknowledge Classification: Tier {tier}\n\n"
                f"### Definition\n{description}\n\n"
                f"### Evidence Required\n"
                f"- Acquisition type: [direct_admission/documentary_proof/circumstantial/constructive]\n"
                f"- Temporal proof: [timestamp of knowledge acquisition]\n"
                f"- Source document: [evidence reference]\n\n"
                f"### Legal Significance\n"
                f"- Distinguishes premeditated action from nescient participation\n"
                f"- Relevant to: intent, conspiracy, aiding and abetting\n"
                f"- Burden: [who bears burden of proving/disproving knowledge]\n"
            ),
            source="provable-foreknowledge/classification",
            genre_tag="legal reasoning",
        ))

    # Temporal audit trail generation
    samples.append(TrainingSample(
        task="foreknowledge_audit",
        instruction=(
            "Generate a temporally-indexed foreknowledge audit trail for the following scenario. "
            "Track which agents knew which material facts, when they learned them, and the evidence proving it."
        ),
        response=(
            "## Foreknowledge Audit Trail\n\n"
            "### Material Facts Register\n"
            "| Fact ID | Description | Category | First Known |\n"
            "|---------|-------------|----------|-------------|\n"
            "| MF-001 | [fact] | [category] | [date] |\n\n"
            "### Agent Knowledge Matrix\n"
            "| Agent | MF-001 | MF-002 | MF-003 | Tier |\n"
            "|-------|--------|--------|--------|------|\n"
            "| [name] | [date/unknown] | [date/unknown] | [date/unknown] | [A/B/C/D] |\n\n"
            "### Chronological Audit\n"
            "| Date | Agent | Fact Learned | Acquisition Type | Evidence |\n"
            "|------|-------|-------------|------------------|----------|\n"
            "| [date] | [agent] | [fact_id] | [type] | [doc_ref] |\n\n"
            "### Implications\n"
            "- Agents with Tier A/B classification: [list]\n"
            "- Premeditation indicators: [analysis]\n"
            "- Recommended legal action: [based on foreknowledge evidence]\n"
        ),
        source="provable-foreknowledge/audit_trail",
        genre_tag="legal reasoning",
    ))

    # Knowledge event types
    acquisition_types = [
        ("direct_admission", "Agent explicitly stated knowledge in writing or testimony"),
        ("documentary_proof", "Agent was author, recipient, or signatory of document containing the fact"),
        ("meeting_attendance", "Agent attended meeting where fact was discussed (minutes/agenda prove it)"),
        ("email_cc", "Agent was CC'd or BCC'd on communication containing the fact"),
        ("role_based", "Agent's role required knowledge of the fact (constructive knowledge)"),
        ("public_record", "Fact was in public record accessible to agent"),
    ]

    for acq_type, description in acquisition_types:
        samples.append(TrainingSample(
            task="knowledge_event_analysis",
            instruction=f"Analyze knowledge acquisition event: {acq_type} — {description}",
            response=(
                f"## Knowledge Event: {acq_type.replace('_', ' ').title()}\n\n"
                f"### Description\n{description}\n\n"
                f"### Evidence Strength\n"
                f"- Reliability: [conclusive/strong/moderate/weak]\n"
                f"- Admissibility: [assessment under evidence law]\n"
                f"- Rebuttable: [yes/no — can agent deny knowledge?]\n\n"
                f"### Legal Weight\n"
                f"- Supports intent: [yes/no]\n"
                f"- Supports conspiracy: [yes/no]\n"
                f"- Supports negligence: [yes/no]\n"
            ),
            source="provable-foreknowledge/knowledge_events",
            genre_tag="legal reasoning",
        ))

    print(f"  Extracted {len(samples)} foreknowledge samples")
    return samples


def extract_legal_filing_samples() -> list[TrainingSample]:
    """Extract legal filing generation samples from hyper-holmes templates."""
    samples = []

    filing_types = [
        ("cipc_complaint", "CIPC Complaint", "Companies Act 71 of 2008",
         ["complainant_details", "respondent_details", "company_details",
          "nature_of_complaint", "factual_background", "contraventions",
          "evidence_summary", "relief_sought", "annexures"]),
        ("popia_complaint", "POPIA Complaint", "Protection of Personal Information Act 4 of 2013",
         ["complainant_details", "responsible_party", "personal_information",
          "processing_description", "consent_analysis", "breach_details",
          "harm_suffered", "relief_sought"]),
        ("npa_tax_fraud", "NPA Tax Fraud Report", "Tax Administration Act / Income Tax Act",
         ["suspect_details", "tax_periods", "false_returns", "true_liability",
          "amount_evaded", "method_of_evasion", "evidence_summary", "annexures"]),
        ("commercial_crime", "Commercial Crime Submission", "Prevention of Organised Crime Act",
         ["suspect_details", "offences", "modus_operandi", "financial_impact",
          "evidence_chain", "witness_list", "annexures"]),
        ("affidavit", "Affidavit", "General legal proceedings",
         ["deponent_details", "background", "numbered_facts",
          "evidence_references", "conclusion", "oath"]),
    ]

    for filing_id, filing_name, legislation, sections in filing_types:
        section_text = "\n".join([f"### {i+1}. {s.replace('_', ' ').title()}" for i, s in enumerate(sections)])
        samples.append(TrainingSample(
            task="legal_filing",
            instruction=f"Draft a {filing_name} under {legislation}. Include all required sections.",
            response=(
                f"# {filing_name.upper()}\n"
                f"## {legislation}\n\n"
                f"{section_text}\n\n"
                f"---\n"
                f"*Document standards: Remove hyperbole and speculation. "
                f"Include only verified facts with evidence references. "
                f"Use paragraph-by-paragraph format with proper numbering. "
                f"Every claim must link to an annexure reference.*\n"
            ),
            source=f"hyper-holmes/templates/{filing_id}",
            genre_tag="legal drafting",
        ))

    print(f"  Extracted {len(samples)} legal filing samples")
    return samples


# ── Main Pipeline ──


def main():
    parser = argparse.ArgumentParser(description="Prepare LEX legal training data for Erebus 350M")
    parser.add_argument("--repo-dir", type=str, help="Path to ad-res-j7 repository")
    parser.add_argument("--skills-dir", type=str, default="/home/ubuntu/skills",
                        help="Path to skills directory")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory for training data")
    parser.add_argument("--all", action="store_true", help="Extract from all sources")
    parser.add_argument("--format", choices=["erebus", "instruction", "chat", "all"],
                        default="all", help="Output format")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    skills_dir = Path(args.skills_dir)

    print("=" * 60)
    print("LEX Legal Training Data Preparation")
    print("=" * 60)

    all_samples: list[TrainingSample] = []

    # Extract from all sources
    print("\n[1/5] Entity-Relation samples...")
    if args.repo_dir:
        all_samples.extend(extract_entity_relation_samples(Path(args.repo_dir)))
    else:
        # Generate from skill knowledge alone
        all_samples.extend(extract_entity_relation_samples(Path("/dev/null")))

    print("[2/5] Evidence chain samples...")
    all_samples.extend(extract_evidence_chain_samples(skills_dir))

    print("[3/5] Burden of proof samples...")
    all_samples.extend(extract_burden_of_proof_samples(skills_dir))

    print("[4/5] Foreknowledge samples...")
    all_samples.extend(extract_foreknowledge_samples(skills_dir))

    print("[5/5] Legal filing samples...")
    all_samples.extend(extract_legal_filing_samples())

    print(f"\nTotal samples: {len(all_samples)}")

    # Write outputs
    if args.format in ("erebus", "all"):
        erebus_path = output_dir / "train_erebus.txt"
        with open(erebus_path, "w") as f:
            for sample in all_samples:
                f.write(sample.to_erebus_format())
                f.write("\n<|endoftext|>\n")
        print(f"  Wrote Erebus format: {erebus_path}")

    if args.format in ("instruction", "all"):
        instr_path = output_dir / "train_instruction.jsonl"
        with open(instr_path, "w") as f:
            for sample in all_samples:
                f.write(json.dumps(sample.to_instruction_format()) + "\n")
        print(f"  Wrote instruction format: {instr_path}")

    if args.format in ("chat", "all"):
        chat_path = output_dir / "train_chat.jsonl"
        with open(chat_path, "w") as f:
            for sample in all_samples:
                f.write(json.dumps(sample.to_chat_format()) + "\n")
        print(f"  Wrote chat format: {chat_path}")

    # Write metadata
    meta = {
        "total_samples": len(all_samples),
        "task_distribution": {},
        "source_distribution": {},
    }
    for s in all_samples:
        meta["task_distribution"][s.task] = meta["task_distribution"].get(s.task, 0) + 1
        meta["source_distribution"][s.source] = meta["source_distribution"].get(s.source, 0) + 1

    meta_path = output_dir / "metadata.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  Wrote metadata: {meta_path}")

    print(f"\nTask distribution:")
    for task, count in sorted(meta["task_distribution"].items()):
        print(f"  {task}: {count}")

    print("\nDone!")


if __name__ == "__main__":
    main()
