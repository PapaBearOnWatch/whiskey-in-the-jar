# Whiskey in the Jar
### Local Email Analysis and Threat Intelligence

- **Version:** 0.1.0
- **Status:** Functional MVP
- **Language:** Python
- **Database:** SQLite

## Overview

Whiskey in the Jar is a locally operated email analysis tool designed to identify suspicious characteristics in email messages and examine relationships between multiple messages.

It combines email collection, indicator extraction, rule-based analysis, relationship assessment, and intelligence reporting in a desktop application and command-line workflow.

The project demonstrates a practical threat intelligence workflow:

1. Collect email samples.
2. Extract message information and indicators.
3. Analyze suspicious characteristics.
4. Compare messages for recurring patterns.
5. Group potentially related messages.
6. Produce intelligence reports.

## Current Capabilities

### Email Collection
- Accepts `.eml` files.
- Preserves original email bytes in CLI mode.
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
- Documents supporting evidence and analytical limitations.

### Desktop Application
- Graphical interface for working with email samples.
- Private Session Mode using a temporary working directory and SQLite database.
- Session cleanup when the application closes.
- Recovery of abandoned session directories after an interrupted session.
- Standalone Windows desktop build.

## Requirements

- Python 3.13 or compatible version.
- Windows, macOS, or Linux for the Python workflows.
- SQLite (included with Python).
- Third-party packages listed in `requirements.txt`.

The packaged desktop executable is currently built for Windows.

## Installation

1. Download or clone the repository.
2. Open a terminal in the project directory.
3. Create a virtual environment:

    `python -m venv .venv`

4. Activate it in PowerShell:

    `.venv\Scripts\Activate.ps1`

5. Install dependencies:

    `pip install -r requirements.txt`

## Using the Desktop Application

To launch the desktop application from Python:

    python desktop.py

The Windows packaged application can be built using:

    python -m PyInstaller --clean WhiskeyInTheJar.spec

The resulting application is located in:

    dist/WhiskeyInTheJar/WhiskeyInTheJar.exe

## Private Session Mode

The desktop application provides a Private Session Mode designed to keep an analysis session separate from the persistent command-line database.

During a private session:

- A temporary working directory is created.
- A separate SQLite database is used.
- Session files are cleaned up when the application closes normally.
- Abandoned session directories are checked during startup and cleaned up when they can safely be accessed.

Private Session Mode is designed to limit the retention of analyzed email data between sessions.

Directory cleanup should not be interpreted as a guarantee of forensic-grade data erasure.

## Using the Command-Line Interface

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

The CLI workflow uses the persistent SQLite database.

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

- URLs are extracted but never automatically visited.
- Attachments are not automatically opened or executed.
- No automatic replies are sent.
- No messages are automatically deleted, blocked, or quarantined.
- Analysis results are stored locally in SQLite.
- CLI mode preserves original email data in its persistent database.
- Desktop Private Session Mode uses a separate temporary database.

## Current Limitations

This is a functional MVP, not a production email security platform.

- No direct Gmail or Outlook integration.
- No automatic inbox monitoring.
- No automated threat response.
- No attachment analysis.
- No authentication-header analysis.
- Email body analysis currently focuses on plain-text content.
- Brand-domain checks cover a limited configured list.
- Risk scoring is heuristic and requires human review.
- Relationship analysis does not establish attribution or campaign ownership.
- Individual email reports are generated through the command-line workflow.
- Cluster analysis currently uses separate demonstration scripts.
- The packaged desktop application currently targets Windows.

## Project Goals

Whiskey in the Jar demonstrates practical work with:

- Email threat analysis.
- Indicator extraction.
- Static analysis.
- Threat intelligence correlation.
- Pattern recognition.
- Analytical reporting.
- Python and SQLite application development.
- Desktop application packaging.
- Privacy-conscious local data handling.

The emphasis is on practical analysis, explainable findings, and responsible interpretation of evidence.

---

**Whiskey in the Jar**

*Local email analysis. Evidence before assumptions.*