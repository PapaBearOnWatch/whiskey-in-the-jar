from datetime import datetime
from pathlib import Path

from intelligence.pattern_analysis import (
    analyze_domain_patterns,
    identify_email_clusters,
    generate_cluster_reports,
)
from intelligence.relationship_assessment import assess_cluster

domain = "example.invalid"

comparisons = analyze_domain_patterns(domain)
clusters = identify_email_clusters(comparisons)
reports = generate_cluster_reports(domain, clusters, comparisons)

if not reports:
    raise SystemExit("No clusters found. No report was generated.")

lines = [
    "# Whiskey in the Jar",
    "## Email Intelligence Report",
    "",
    f"**Domain analyzed:** {domain}",
    f"**Report generated:** {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}",
    "**Data source:** Synthetic test emails",
    "**Analysis type:** Static email and relationship analysis",
    "",
    "---",
    "",
    "## Executive Summary",
    "",
    f"Analysis identified **{len(reports)} cluster(s)** for the domain.",
    "",
    "These groupings identify patterns for further review. They do not, by themselves, establish malicious intent, common ownership, coordination, or campaign activity.",
    "",
]

for report in reports:
    assessment = assess_cluster(report)

    lines.extend([
        "---",
        "",
        f"## Cluster {report['cluster_id']}",
        "",
        "### Cluster Assessment",
        "",
        f"**Classification: {assessment['classification']}**",
        "",
        assessment["explanation"],
        "",
        "**Supporting evidence:**",
        "",
    ])

    lines.extend(f"- {item}" for item in assessment["evidence"])

    lines.extend([
        "",
        "**Individual message risk summary:**",
        "",
    ])

    lines.extend(
        f"- {level}: {count}"
        for level, count in assessment["risk_summary"].items()
    )

    lines.extend([
        "",
        "**Assessment caveat:**",
        "",
        assessment["caveat"],
        "",
        "### Message Details",
        "",
        f"- **Messages:** {report['message_count']}",
        f"- **Senders:** {len(report['senders'])}",
        "",
        "**Observed senders:**",
        "",
    ])

    lines.extend(f"- {sender}" for sender in report["senders"])

    lines.extend(["", "**Observed subjects:**", ""])
    lines.extend(f"- {subject}" for subject in report["subjects"])

    lines.extend(["", "**Timestamps:**", ""])
    lines.extend(f"- {timestamp}" for timestamp in report["timestamps"])

    lines.extend([
        "",
        "### Infrastructure and URL Relationships",
        "",
        f"- Shared protocols: {', '.join(report['shared_protocols']) or 'None observed'}",
        f"- Shared hosts: {', '.join(report['shared_hosts']) or 'None observed'}",
        f"- Shared paths: {', '.join(report['shared_paths']) or 'None observed'}",
        f"- Identical URLs: {', '.join(report['identical_urls']) or 'None observed'}",
        "",
        "**URL relationship counts:**",
        "",
    ])

    for relationship, count in report["url_relationships"].items():
        lines.append(f"- {relationship.replace('_', ' ').capitalize()}: {count}")

    lines.extend([
        "",
        "### Subject Similarity and Group Cohesion",
        "",
        f"- Average subject similarity: {report['average_subject_similarity']}",
        f"- Minimum subject similarity: {report['minimum_subject_similarity']}",
        f"- Qualifying pairs: {report['qualifying_pair_count']}",
        f"- Possible pairs: {report['possible_pair_count']}",
        f"- Pair coverage: {report['pair_coverage_percent']}%",
        f"- Grouping basis: {report['grouping_basis']}",
        "",
    ])

lines.extend([
    "---",
    "",
    "## Methodology and Limitations",
    "",
    "- Analysis is performed locally against stored email data.",
    "- Message content and URLs are examined statically; destination URLs are not visited.",
    "- Relationship groupings use sender differences, subject similarity, and timing.",
    "- Shared infrastructure is an observation, not proof of a relationship.",
    "- Individual message risk assessments remain separate from cluster-level assessments.",
    "- Findings are heuristic assessments and require human review.",
    "",
    "## Report Status",
    "",
    "This report was generated from synthetic test data for demonstration and validation. It is not a report of live threat activity.",
    "",
])

output_path = Path("reports") / "whiskey_intelligence_report_example.invalid.md"
output_path.write_text("\n".join(lines), encoding="utf-8")

print(f"Report generated: {output_path}")
print(f"Clusters included: {len(reports)}")
