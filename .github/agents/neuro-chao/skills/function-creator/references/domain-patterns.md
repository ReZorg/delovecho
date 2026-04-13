# Domain Mapping Patterns

## Table of Contents

1. [Financial Domain Family](#financial-domain-family)
2. [Data Sync Domain Family](#data-sync-domain-family)
3. [Document Processing Family](#document-processing-family)
4. [Investigation Domain Family](#investigation-domain-family)
5. [Platform Integration Family](#platform-integration-family)
6. [Writing Your Own Mappings](#writing-your-own-mappings)

## Financial Domain Family

Source domain: **Banking / Statements**

| Source Term | → Stock Market | → Crypto | → Insurance | → Real Estate |
|-------------|---------------|----------|-------------|---------------|
| bank | brokerage | exchange | insurer | agency |
| statement | portfolio report | wallet report | policy summary | property report |
| transaction | trade | swap/transfer | claim | closing |
| balance | portfolio value | wallet balance | coverage amount | equity |
| account | trading account | wallet | policy | listing |
| debit | sell | send | premium | expense |
| credit | buy | receive | payout | income |
| interest | dividend | yield/APY | premium rate | appreciation |
| fee | commission | gas fee | deductible | closing cost |

## Data Sync Domain Family

Source domain: **Email / Mailbox Sync**

| Source Term | → CRM Sync | → File Sync | → Database Sync | → Chat Sync |
|-------------|-----------|------------|----------------|------------|
| mailbox | account | drive | database | workspace |
| message | record | file | row | message |
| folder | pipeline stage | directory | table | channel |
| attachment | document | embedded file | blob | media |
| sender | owner | author | writer | sender |
| recipient | assignee | shared-with | reader | recipient |
| subject | title | filename | primary key | topic |
| read/unread | open/new | accessed/new | processed/pending | read/unread |
| delta sync | change tracking | diff sync | CDC | event stream |
| Graph API | REST API | WebDAV | DB protocol | WebSocket |

## Document Processing Family

Source domain: **PDF Statement Extraction**

| Source Term | → Image OCR | → Audio Transcription | → Video Analysis | → Web Scraping |
|-------------|-----------|---------------------|-----------------|---------------|
| PDF | image | audio file | video | webpage |
| page | region | segment | frame | section |
| text extraction | OCR | speech-to-text | frame analysis | DOM parsing |
| table | grid/matrix | structured data | scene | HTML table |
| header/footer | watermark | intro/outro | title card | nav/footer |
| field | bounding box | utterance | object | element |
| validate | verify | proofread | review | check |
| schema | template | transcript format | annotation schema | selector map |

## Investigation Domain Family

Source domain: **Legal Case Analysis**

| Source Term | → Security Audit | → Bug Investigation | → Fraud Detection | → Research |
|-------------|-----------------|--------------------|--------------------|-----------|
| case | audit | incident | investigation | study |
| evidence | finding | log/trace | indicator | data point |
| witness | informant | reporter | whistleblower | source |
| filing | report | ticket | alert | publication |
| court | review board | triage | compliance | peer review |
| judgment | verdict | resolution | determination | conclusion |
| burden of proof | confidence level | reproduction steps | evidence threshold | significance |
| entity | asset/actor | component | account/entity | subject |
| timeline | audit trail | event log | transaction history | chronology |

## Platform Integration Family

Source domain: **Exchange Online / Microsoft 365**

| Source Term | → Google Workspace | → Slack | → Notion | → GitHub |
|-------------|-------------------|---------|----------|----------|
| Exchange Online | Gmail/Calendar | Slack | Notion | GitHub |
| Graph API | Google API | Slack API | Notion API | GitHub API |
| mailbox | inbox | channel | database | repository |
| calendar | calendar | reminder | calendar DB | project board |
| contact | contact | member | person | collaborator |
| tenant | organization | workspace | workspace | organization |
| OAuth/Entra | OAuth/Google | OAuth/Slack | OAuth/Notion | OAuth/GitHub |
| delta query | push notification | event subscription | webhook | webhook |

## Writing Your Own Mappings

### Step 1: Identify the Source Vocabulary

List all domain-specific terms in the source skill:
- Nouns (entities, objects, concepts)
- Verbs (actions, operations, processes)
- Services (APIs, platforms, tools)
- Formats (data types, file formats, protocols)

### Step 2: Find Analogous Terms

For each source term, find the target domain equivalent by asking:
- "What plays the same **role** in the target domain?"
- "What has the same **relationships** to other concepts?"
- "What undergoes the same **operations**?"

### Step 3: Validate the Mapping

Check that the mapping preserves relationships:
- If A contains B in source, mapped-A should contain mapped-B
- If A produces B in source, mapped-A should produce mapped-B
- If A validates B in source, mapped-A should validate mapped-B

### Step 4: Document Gaps

Not every term maps cleanly. Document:
- **Missing concepts**: Target domain lacks an equivalent
- **Split concepts**: One source term maps to multiple target terms
- **Merged concepts**: Multiple source terms map to one target term
- **Novel concepts**: Target domain has concepts with no source equivalent

These gaps indicate where the transformed skill needs manual customization.
