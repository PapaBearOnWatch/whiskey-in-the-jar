# Whiskey in the Jar
### Local Email Analysis and Threat Intelligence

- **Version:** 0.1.0
- **Status:** Functional MVP
- **Language:** Python
**Database:** SQLite

## Overview

Whiskey in the Jar is a locally operated email analysis tool designed to identify suspicious characteristics in email messages and examine relationships between multiple messages.

It demonstrates a basic threat intelligence workflow:

1. Collect and preserve email samples.
2. Extract message information and indicators.
3. Analyze suspicious characteristics.
4. Compare messages for recurring patterns.
5. Group potentially related messages.
6. Produce intelligence reports.

## Current Capabilities

### Email Collection
- Accepts .eml files.
- Preserves original email bytes.
- Extracts sender, recipient, subject, date, and message ID.
- Calculates SHA-256 fingerprints.
- Detects duplicate messages.
- Enforces a 10 MB size limit.

### Email Analysis
- Identifies suspicious urgency language.
- Checks selected brand display names against trusted domains.
- Extracts URLs and domains.
- Identifies HTTP URLs, URL user information, punycode, known shorteners, and IP-address URLs.
- Assigns preliminary LOW, MEDIUM, or HIGH risk levels.

### Relationship Analysis
- Compares messages for shared URL characteristics.
- Examines sender differences, subject similarity, and timing.
- Identifies groups meeting defined similarity criteria.
- Calculates cluster cohesion.
- Produces heuristic relationship assessments.

### Reporting
- Generates individual Markdown reports.
- Generates cluster reports using synthetic demonstration data.
- Documents supporting evidence and limitations.


## Requirements

- Python 3.13 or compatible version.
- Windows, macOS, or Linux.
- SQLite (included with Python).
- No third-party Python packages currently required.

## Installation

1. Download or clone the repository.
2. Open a terminal in the project directory.
3. Create a virtual environment:

    python -m venv .venv

4. Activate it in PowerShell:

    .venv\Scripts\Activate.ps1

5. Initialize the database:

    python database/init_db.py


## Using Whiskey

Save an email message as an `.eml` file.

Run the following command, replacing the path with your email's location:

    python whiskey.py analyze "C:\Path\To\suspicious_email.eml"

Whiskey will:

1. Read the supplied email.
2. Check whether it is a duplicate.
3. Store the original message if it is new.
4. Analyze the message.
5. Save the analysis results.
6. Generate a Markdown report.

Reports are saved in the `reports` directory.

## Relationship Analysis

The project includes synthetic test data for demonstrating relationship analysis.

Generate the example cluster report with:

    python generate_report.py

The demonstration uses the reserved `example.invalid` domain and synthetic messages.


## Analytical Approach

Whiskey uses deterministic, rule-based indicators and heuristic comparisons.

Risk levels are preliminary assessments, not definitive verdicts.

Relationship classifications describe observed similarities. They do not prove common ownership, coordination, or malicious activity.

Individual message risk and cluster-level assessments are deliberately kept separate.

## Security and Safety

Whiskey is designed for static analysis.

- Original email data is preserved.
- URLs are extracted but never automatically visited.
- Attachments are not automatically opened or executed.
- No automatic replies are sent.
- No messages are automatically deleted, blocked, or quarantined.
- Analysis results are stored locally in SQLite.

## Current Limitations

This is a functional MVP, not a production email security platform.

- No direct Gmail or Outlook integration.
- No automatic inbox monitoring.
- No graphical user interface.
- No automated threat response.
- No attachment analysis.
- No authentication-header analysis.
- Email body analysis currently focuses on plain-text content.
- Brand-domain checks cover a limited configured list.
- Risk scoring is heuristic and requires human review.
- Relationship analysis does not establish attribution or campaign ownership.
- Individual email reports are generated through the command-line workflow. Cluster analysis currently uses separate demonstration scripts.

## Project Goals

Whiskey in the Jar demonstrates practical work with:

- Email threat analysis.
- Indicator extraction.
- Static analysis.
- Threat intelligence correlation.
- Pattern recognition.
- Analytical reporting.
- Python and SQLite application development.

The emphasis is on practical analysis, explainable findings, and responsible interpretation of evidence.

---

**Whiskey in the Jar**

*Local email analysis. Evidence before assumptions.*
