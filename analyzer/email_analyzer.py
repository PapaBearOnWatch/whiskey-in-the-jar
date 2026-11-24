import re
import json
from email import policy
from email.parser import BytesParser
from urllib.parse import urlparse

from database.init_db import get_connection
from config import BRAND_DOMAINS


URGENCY_PHRASES = [
    "immediate action required",
    "account suspended",
    "account will be closed",
    "verify your account",
    "urgent action",
    "unusual activity",
    "payment failed",
    "password expires",
    "act now",
    "within 24 hours",
]

URL_PATTERN = re.compile(
    r'https?://[^\s<>"\']+',
    re.IGNORECASE
)

SHORTENERS = [
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "is.gd",
    "ow.ly",
]


def extract_body(message):
    parts = []

    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                if part.get_content_disposition() != "attachment":
                    try:
                        parts.append(part.get_content())
                    except Exception:
                        continue
    else:
        if message.get_content_type() == "text/plain":
            try:
                parts.append(message.get_content())
            except Exception:
                pass

    return "\n".join(parts)


def analyze_email(email_id):
    with get_connection() as connection:
        email_record = connection.execute(
            "SELECT * FROM emails WHERE id = ?",
            (email_id,)
        ).fetchone()

    if not email_record:
        raise ValueError(f"Email ID {email_id} not found.")

    raw_email = email_record["raw_email"]
    parsing_copy = raw_email.removeprefix(b"\xef\xbb\xbf")

    message = BytesParser(
        policy=policy.default
    ).parsebytes(parsing_copy)

    sender = email_record["sender"] or ""
    subject = email_record["subject"] or ""
    body = extract_body(message)

    findings = []
    indicators = []
    score = 0

    combined_text = f"{subject} {body}".lower()

    for phrase in URGENCY_PHRASES:
        if phrase in combined_text:
            findings.append({
                "type": "urgency_language",
                "description": f"Potentially suspicious phrase: {phrase}"
            })
            score += 2

    sender_match = re.search(r'<([^<>]+)>', sender)

    if sender_match:
        display_name = sender.split("<")[0].strip().strip('"')
        email_address = sender_match.group(1).strip()
        sender_domain = email_address.rsplit("@", 1)[-1].lower()

        for brand, trusted_domains in BRAND_DOMAINS.items():
            if brand in display_name.lower():
                trusted = any(
                    sender_domain == domain or
                    sender_domain.endswith("." + domain)
                    for domain in trusted_domains
                )

                if not trusted:
                    findings.append({
                        "type": "possible_impersonation",
                        "description": (
                            f"Display name '{display_name}' references "
                            f"{brand.title()}, but sender domain "
                            f"'{sender_domain}' is not on its trusted "
                            "domain list."
                        )
                    })
                    score += 3
                break

    urls = URL_PATTERN.findall(body)

    for url in urls:
        url = url.rstrip(".,;:!?)")
        parsed = urlparse(url)
        hostname = parsed.hostname or ""

        indicators.append({
            "type": "url",
            "value": url
        })

        if hostname:
            indicators.append({
                "type": "domain",
                "value": hostname.lower()
            })

        if parsed.scheme != "https":
            findings.append({
                "type": "unencrypted_url",
                "description": "URL does not use HTTPS."
            })
            score += 1

        if "@" in parsed.netloc:
            findings.append({
                "type": "url_userinfo",
                "description": "URL contains user information before its host."
            })
            score += 3

        if hostname.lower().startswith("xn--") or ".xn--" in hostname.lower():
            findings.append({
                "type": "punycode_domain",
                "description": "URL contains a punycode domain."
            })
            score += 3

        if hostname.lower() in SHORTENERS:
            findings.append({
                "type": "shortened_url",
                "description": f"URL uses a shortening service: {hostname}"
            })
            score += 2

        if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", hostname):
            findings.append({
                "type": "ip_address_url",
                "description": "URL uses an IP address instead of a domain."
            })
            score += 3

    if score >= 7:
        risk_level = "HIGH"
    elif score >= 3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    result = {
        "email_id": email_id,
        "risk_level": risk_level,
        "score": score,
        "findings": findings,
        "indicators": indicators,
        "url_count": len(urls),
        "assessment": (
            "Preliminary indicator-based assessment. "
            "This is not a definitive phishing verdict."
        )
    }

    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM analysis_results
            WHERE id NOT IN (
                SELECT MAX(id)
                FROM analysis_results
                GROUP BY email_id
            )
            """
        )

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_analysis_email_unique
            ON analysis_results(email_id)
            """
        )

        connection.execute(
            """
            INSERT INTO analysis_results (
                email_id, risk_level, findings
            )
            VALUES (?, ?, ?)
            ON CONFLICT(email_id) DO UPDATE SET
                risk_level = excluded.risk_level,
                findings = excluded.findings,
                analyzed_at = CURRENT_TIMESTAMP
            """,
            (email_id, risk_level, json.dumps(result, indent=2))
        )

        connection.execute(
            "DELETE FROM indicators WHERE email_id = ?",
            (email_id,)
        )

        for indicator in indicators:
            connection.execute(
                """
                INSERT INTO indicators (
                    email_id, indicator_type, indicator_value
                )
                VALUES (?, ?, ?)
                """,
                (email_id, indicator["type"], indicator["value"])
            )

    return result
