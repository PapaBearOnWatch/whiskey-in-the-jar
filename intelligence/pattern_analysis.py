import re
from itertools import combinations
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

from database.init_db import get_connection


def extract_sender_address(sender):
    match = re.search(r'<([^<>]+)>', sender or "")
    if match:
        return match.group(1).strip().lower()
    return (sender or "").strip().lower()


def parse_received_date(date_value):
    if not date_value:
        return None

    try:
        return parsedate_to_datetime(date_value)
    except (TypeError, ValueError, OverflowError):
        return None


def extract_subject_words(subject):
    words = re.findall(r'\b[a-z0-9]+\b', (subject or "").lower())
    return set(words)


def compare_subjects(subject_a, subject_b):
    words_a = extract_subject_words(subject_a)
    words_b = extract_subject_words(subject_b)

    if not words_a or not words_b:
        return 0.0

    shared = words_a.intersection(words_b)
    combined = words_a.union(words_b)

    return len(shared) / len(combined)


def analyze_domain_patterns(domain):
    domain = domain.strip().lower()

    if not domain:
        raise ValueError("A domain must be supplied.")

    with get_connection() as connection:
        emails = connection.execute(
            """
            SELECT DISTINCT
                e.id,
                e.sender,
                e.subject,
                e.received_at,
                a.risk_level
            FROM indicators i
            JOIN emails e ON e.id = i.email_id
            LEFT JOIN analysis_results a ON a.email_id = e.id
            WHERE i.indicator_type = 'domain'
              AND LOWER(i.indicator_value) = ?
            ORDER BY e.id
            """,
            (domain,)
        ).fetchall()

        urls = connection.execute(
            """
            SELECT DISTINCT
                i.email_id,
                i.indicator_value
            FROM indicators i
            JOIN emails e ON e.id = i.email_id
            WHERE i.indicator_type = 'url'
              AND EXISTS (
                  SELECT 1
                  FROM indicators d
                  WHERE d.email_id = i.email_id
                    AND d.indicator_type = 'domain'
                    AND LOWER(d.indicator_value) = ?
              )
            """,
            (domain,)
        ).fetchall()

    email_records = [dict(email) for email in emails]

    protocols_by_email = {}
    urls_by_email = {}

    for row in urls:
        parsed = urlparse(row["indicator_value"])

        protocols_by_email.setdefault(row["email_id"], set()).add(
            parsed.scheme.lower()
        )

        urls_by_email.setdefault(row["email_id"], []).append(
            row["indicator_value"]
        )

    comparisons = []

    for email_a, email_b in combinations(email_records, 2):
        sender_a = extract_sender_address(email_a["sender"])
        sender_b = extract_sender_address(email_b["sender"])

        date_a = parse_received_date(email_a["received_at"])
        date_b = parse_received_date(email_b["received_at"])

        time_difference = None

        if date_a and date_b:
            time_difference = abs(
                (date_b - date_a).total_seconds()
            ) / 60

        protocols_a = protocols_by_email.get(email_a["id"], set())
        protocols_b = protocols_by_email.get(email_b["id"], set())

        shared_protocols = sorted(protocols_a.intersection(protocols_b))

        url_comparison = compare_url_destinations(
            urls_by_email.get(email_a["id"], []),
            urls_by_email.get(email_b["id"], [])
        )

        subject_similarity = compare_subjects(
            email_a["subject"],
            email_b["subject"]
        )

        comparisons.append({
            "email_ids": [email_a["id"], email_b["id"]],
            "different_senders": bool(sender_a and sender_b and sender_a != sender_b),
            "shared_protocols": shared_protocols,
            "shared_hosts": url_comparison["shared_hosts"],
            "shared_paths": url_comparison["shared_paths"],
            "identical_urls": url_comparison["identical_urls"],
            "minutes_apart": round(time_difference, 1) if time_difference is not None else None,
            "subject_similarity": round(subject_similarity, 2)
        })

    print(f"Pattern analysis completed for {domain}.")
    print(f"Associated emails: {len(email_records)}")
    print(f"Email comparisons: {len(comparisons)}")

    for comparison in comparisons:
        print(comparison)

    return comparisons
def identify_email_clusters(comparisons):
    graph = {}

    for comparison in comparisons:
        if not (
            comparison["different_senders"]
            and comparison["minutes_apart"] is not None
            and comparison["minutes_apart"] <= 60
            and comparison["subject_similarity"] >= 0.5
        ):
            continue

        email_a, email_b = comparison["email_ids"]

        graph.setdefault(email_a, set()).add(email_b)
        graph.setdefault(email_b, set()).add(email_a)

    clusters = []
    visited = set()

    for email_id in graph:
        if email_id in visited:
            continue

        pending = [email_id]
        cluster = set()

        while pending:
            current = pending.pop()

            if current in visited:
                continue

            visited.add(current)
            cluster.add(current)

            pending.extend(graph.get(current, set()) - visited)

        if len(cluster) >= 2:
            clusters.append(sorted(cluster))

    return clusters
def generate_cluster_reports(domain, clusters, comparisons):
    reports = []

    with get_connection() as connection:
        for number, cluster in enumerate(clusters, start=1):
            placeholders = ",".join("?" for _ in cluster)

            rows = connection.execute(
                f"""
                SELECT id, sender, subject, received_at,
                       (SELECT risk_level
                        FROM analysis_results
                        WHERE email_id = emails.id) AS risk_level
                FROM emails
                WHERE id IN ({placeholders})
                ORDER BY received_at
                """,
                tuple(cluster)
            ).fetchall()

            email_details = [dict(row) for row in rows]

            cluster_comparisons = [
                comparison
                for comparison in comparisons
                if all(
                    email_id in cluster
                    for email_id in comparison["email_ids"]
                )
            ]

            shared_protocols = set(
                protocol
                for comparison in cluster_comparisons
                for protocol in comparison["shared_protocols"]
            )

            shared_hosts = set(
                host
                for comparison in cluster_comparisons
                for host in comparison["shared_hosts"]
            )

            shared_paths = set(
                path
                for comparison in cluster_comparisons
                for path in comparison["shared_paths"]
            )

            identical_urls = set(
                url
                for comparison in cluster_comparisons
                for url in comparison["identical_urls"]
            )

            url_relationships = {
                "pairs_sharing_host": sum(
                    bool(comparison["shared_hosts"])
                    for comparison in cluster_comparisons
                ),
                "pairs_sharing_path": sum(
                    bool(comparison["shared_paths"])
                    for comparison in cluster_comparisons
                ),
                "pairs_sharing_identical_url": sum(
                    bool(comparison["identical_urls"])
                    for comparison in cluster_comparisons
                )
            }

            similarities = [
                comparison["subject_similarity"]
                for comparison in cluster_comparisons
            ]

            possible_pair_count = (
                len(cluster) * (len(cluster) - 1) // 2
            )

            qualifying_pair_count = sum(
                comparison["different_senders"]
                and comparison["minutes_apart"] is not None
                and comparison["minutes_apart"] <= 60
                and comparison["subject_similarity"] >= 0.5
                for comparison in cluster_comparisons
            )

            pair_coverage_percent = (
                round(
                    qualifying_pair_count / possible_pair_count * 100,
                    1
                )
                if possible_pair_count else None
            )

            minimum_subject_similarity = (
                round(min(similarities), 2)
                if similarities else None
            )
            reports.append({
                "cluster_id": number,
                "domain": domain,
                "message_count": len(email_details),
                "senders": sorted({
                    extract_sender_address(email["sender"])
                    for email in email_details
                    if email["sender"]
                }),
                "subjects": [
                    email["subject"] for email in email_details
                ],
                "timestamps": [
                    email["received_at"] for email in email_details
                ],
                "risk_levels": [
                    email["risk_level"] for email in email_details
                ],
                "shared_protocols": sorted(shared_protocols),
                "shared_hosts": sorted(shared_hosts),
                "shared_paths": sorted(shared_paths),
                "identical_urls": sorted(identical_urls),
                "url_relationships": url_relationships,
                "average_subject_similarity": (
                    round(sum(similarities) / len(similarities), 2)
                    if similarities else None
                ),
                "minimum_subject_similarity": minimum_subject_similarity,
                "qualifying_pair_count": qualifying_pair_count,
                "possible_pair_count": possible_pair_count,
                "pair_coverage_percent": pair_coverage_percent,
                "grouping_basis": (
                    "Different sender addresses, subject similarity "
                    "of at least 0.50, and observation within 60 minutes."
                ),
                "caveat": (
                    "A cluster represents messages meeting defined "
                    "similarity criteria. It does not establish common "
                    "ownership, coordination, or campaign activity."
                )
            })

    return reports

def normalize_url(url):
    if not isinstance(url, str) or not url.strip():
        return None

    try:
        parsed = urlparse(url.strip())

        if parsed.scheme.lower() not in ("http", "https"):
            return None

        if not parsed.hostname:
            return None

        port = parsed.port

        if (
            (parsed.scheme.lower() == "http" and port == 80)
            or (parsed.scheme.lower() == "https" and port == 443)
        ):
            port = None

        return (
            parsed.scheme.lower(),
            parsed.hostname.lower(),
            port,
            parsed.path.rstrip("/") or "/",
            parsed.query,
            parsed.fragment
        )

    except (AttributeError, TypeError, ValueError):
        return None


def format_normalized_url(normalized):
    scheme, host, port, path, query, fragment = normalized

    if ":" in host and not host.startswith("["):
        host = f"[{host}]"

    netloc = host

    if port is not None:
        netloc += f":{port}"

    formatted = f"{scheme}://{netloc}{path}"

    if query:
        formatted += f"?{query}"

    if fragment:
        formatted += f"#{fragment}"

    return formatted


def compare_url_destinations(urls_a, urls_b):
    normalized_a = {
        result for url in urls_a
        if (result := normalize_url(url)) is not None
    }

    normalized_b = {
        result for url in urls_b
        if (result := normalize_url(url)) is not None
    }

    hosts_a = {url[1] for url in normalized_a}
    hosts_b = {url[1] for url in normalized_b}

    paths_a = {url[3] for url in normalized_a}
    paths_b = {url[3] for url in normalized_b}

    return {
        "shared_hosts": sorted(hosts_a.intersection(hosts_b)),
        "shared_paths": sorted(paths_a.intersection(paths_b)),
        "identical_urls": sorted(format_normalized_url(url) for url in normalized_a.intersection(normalized_b))
    }
