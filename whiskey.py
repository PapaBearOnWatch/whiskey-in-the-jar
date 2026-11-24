import argparse
import sys
from datetime import datetime
from pathlib import Path

from collector.email_ingest import ingest_email
from analyzer.email_analyzer import analyze_email
from database.init_db import get_connection, initialize_database


def analyze_file(file_path):
    source = Path(file_path).expanduser()

    if not source.exists():
        raise FileNotFoundError(f"Email file not found: {source}")

    if not source.is_file():
        raise ValueError("The supplied path is not a file.")

    raw_email = source.read_bytes()

    ingestion = ingest_email(raw_email)
    email_id = ingestion["email_id"]

    print(f"\nIngestion status: {ingestion['status']}")
    print(f"Email ID: {email_id}")

    result = analyze_email(email_id)

    with get_connection() as connection:
        email = connection.execute(
            "SELECT sender, recipient, subject, received_at, sha256 "
            "FROM emails WHERE id = ?",
            (email_id,)
        ).fetchone()

    if not email:
        raise RuntimeError("Could not retrieve the stored email.")

    lines = [
        "# Whiskey in the Jar",
        "## Individual Email Analysis",
        "",
        f"**Analysis date:** {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}",
        f"**Source file:** {source.name}",
        f"**Email ID:** {email_id}",
        f"**SHA-256:** {email['sha256']}",
        "",
        "---",
        "",
        "## Email Details",
        "",
        f"- **From:** {email['sender'] or 'Not available'}",
        f"- **To:** {email['recipient'] or 'Not available'}",
        f"- **Subject:** {email['subject'] or 'Not available'}",
        f"- **Date:** {email['received_at'] or 'Not available'}",
        "",
        "## Analytical Assessment",
        "",
        f"**Risk level: {result['risk_level']}**",
        "",
        f"**Indicator score:** {result['score']}",
        "",
        result["assessment"],
        "",
        f"**URLs identified:** {result['url_count']}",
        "",
        "### Findings",
        "",
    ]

    if result["findings"]:
        for finding in result["findings"]:
            lines.append(
                f"- **{finding['type']}**: {finding['description']}"
            )
    else:
        lines.append("No suspicious indicators identified by the current rules.")

    lines.extend(["", "### Extracted Indicators", ""])

    if result["indicators"]:
        for indicator in result["indicators"]:
            lines.append(
                f"- **{indicator['type']}**: `{indicator['value']}`"
            )
    else:
        lines.append("No URL or domain indicators extracted.")

    lines.extend([
        "",
        "---",
        "",
        "## Important Limitations",
        "",
        "- This is a preliminary, rule-based assessment, not a definitive phishing verdict.",
        "- Absence of detected indicators does not establish that an email is safe.",
        "- URLs were extracted but not visited.",
        "- Attachments were not opened or executed.",
        "- Findings require human review and additional context.",
        "",
        "## Report Status",
        "",
        "This report was generated locally by Whiskey in the Jar.",
        "",
    ])

    output_dir = Path(__file__).resolve().parent / "reports"
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / f"email_{email_id}_analysis.md"
    output_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Risk level: {result['risk_level']}")
    print(f"Findings: {len(result['findings'])}")
    print(f"URLs identified: {result['url_count']}")
    print(f"\nReport saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Whiskey in the Jar - Local Email Analysis"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Ingest and analyze an .eml email file"
    )

    analyze_parser.add_argument(
        "file",
        help="Path to the .eml file"
    )

    args = parser.parse_args()

    initialize_database()

    if args.command == "analyze":
        analyze_file(args.file)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, TypeError) as error:
        print(f"\nWhiskey error: {error}", file=sys.stderr)
        sys.exit(1)
