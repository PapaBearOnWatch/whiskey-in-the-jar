import json
from database.init_db import get_connection


def lookup_domain(domain):
    domain = domain.strip().lower()

    if not domain:
        raise ValueError("A domain must be supplied.")

    with get_connection() as connection:
        summary = connection.execute(
            """
            SELECT
                COUNT(DISTINCT e.id) AS email_count,
                MIN(COALESCE(NULLIF(e.received_at, ''), e.created_at))
                    AS first_seen,
                MAX(COALESCE(NULLIF(e.received_at, ''), e.created_at))
                    AS last_seen,
                COUNT(DISTINCT e.sender) AS distinct_senders,
                MAX(
                    CASE a.risk_level
                        WHEN 'HIGH' THEN 3
                        WHEN 'MEDIUM' THEN 2
                        WHEN 'LOW' THEN 1
                        ELSE 0
                    END
                ) AS highest_risk_rank
            FROM indicators i
            JOIN emails e ON e.id = i.email_id
            LEFT JOIN analysis_results a ON a.email_id = e.id
            WHERE i.indicator_type = 'domain'
              AND LOWER(i.indicator_value) = ?
            """,
            (domain,)
        ).fetchone()

        emails = connection.execute(
            """
            SELECT DISTINCT
                e.id,
                e.sender,
                e.subject,
                e.received_at,
                a.risk_level,
                a.findings
            FROM indicators i
            JOIN emails e ON e.id = i.email_id
            LEFT JOIN analysis_results a ON a.email_id = e.id
            WHERE i.indicator_type = 'domain'
              AND LOWER(i.indicator_value) = ?
            ORDER BY e.id
            """,
            (domain,)
        ).fetchall()

        indicator_types = connection.execute(
            """
            SELECT DISTINCT indicator_type
            FROM indicators
            WHERE email_id IN (
                SELECT email_id
                FROM indicators
                WHERE indicator_type = 'domain'
                  AND LOWER(indicator_value) = ?
            )
            ORDER BY indicator_type
            """,
            (domain,)
        ).fetchall()

    email_results = []
    sender_names = set()
    sender_addresses = set()
    risk_scores = []

    for email in emails:
        record = dict(email)

        sender = record["sender"] or ""
        if "<" in sender and ">" in sender:
            display_name = sender.split("<", 1)[0].strip().strip('"')
            address = sender.split("<", 1)[1].split(">", 1)[0].strip()
        else:
            display_name = sender
            address = sender

        if display_name:
            sender_names.add(display_name)

        if address:
            sender_addresses.add(address.lower())

        findings_data = json.loads(record["findings"]) if record["findings"] else {}
        score = findings_data.get("score", 0)
        risk_scores.append(score)

        record["risk_score"] = score
        record.pop("findings", None)
        email_results.append(record)

    risk_rank = summary["highest_risk_rank"] or 0
    risk_labels = {3: "HIGH", 2: "MEDIUM", 1: "LOW", 0: "UNKNOWN"}

    if summary["email_count"] >= 2 and len(sender_addresses) >= 2:
        relationship = {
            "status": "SHARED DOMAIN ACROSS MULTIPLE SENDERS",
            "observation": (
                f"{summary['email_count']} messages from "
                f"{len(sender_addresses)} distinct sender addresses "
                f"reference this domain."
            ),
            "assessment": (
                "Shared infrastructure warrants further investigation."
            ),
            "caveat": (
                "This association does not establish common control "
                "or prove that the messages belong to the same campaign."
            )
        }
    else:
        relationship = {
            "status": "INSUFFICIENT OBSERVATIONS",
            "observation": (
                "Not enough distinct sender addresses have been "
                "observed to establish a shared-domain relationship."
            ),
            "assessment": "Continue monitoring for additional observations.",
            "caveat": (
                "A lack of observed relationships does not establish "
                "that a domain is safe."
            )
        }

    return {
        "domain": domain,
        "relationship": relationship,
        "email_count": summary["email_count"],
        "distinct_senders": len(sender_addresses),
        "sender_names": sorted(sender_names),
        "highest_risk": risk_labels[risk_rank],
        "highest_risk_score": max(risk_scores, default=0),
        "lowest_risk_score": min(risk_scores, default=0),
        "first_seen": summary["first_seen"],
        "last_seen": summary["last_seen"],
        "indicator_types": [
            row["indicator_type"] for row in indicator_types
        ],
        "emails": email_results
    }
