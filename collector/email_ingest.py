import hashlib
from email import policy
from email.parser import BytesParser

from database.init_db import get_connection


def calculate_hash(raw_email):
    return hashlib.sha256(raw_email).hexdigest()


def ingest_email(raw_email):
    if isinstance(raw_email, str):
        raw_email = raw_email.encode("utf-8")

    if not isinstance(raw_email, bytes):
        raise TypeError("Email must be supplied as bytes or text.")

    if not raw_email.strip():
        raise ValueError("Email cannot be empty.")

    if len(raw_email) > 10 * 1024 * 1024:
        raise ValueError("Email exceeds the 10 MB size limit.")

    # Preserve original bytes; remove BOM only from parsing copy.
    parsing_copy = raw_email.removeprefix(b"\xef\xbb\xbf")

    message = BytesParser(
        policy=policy.default
    ).parsebytes(parsing_copy)

    sender = message.get("From", "")
    recipient = message.get("To", "")
    subject = message.get("Subject", "")
    message_id = message.get("Message-ID", "")
    received_at = message.get("Date", "")

    fingerprint = calculate_hash(raw_email)

    with get_connection() as connection:

        existing = connection.execute(
            "SELECT id FROM emails WHERE sha256 = ?",
            (fingerprint,)
        ).fetchone()

        if existing:
            return {
                "status": "duplicate",
                "email_id": existing["id"],
                "sha256": fingerprint
            }

        cursor = connection.execute(
            """
            INSERT INTO emails (
                message_id,
                sender,
                recipient,
                subject,
                received_at,
                raw_email,
                sha256
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message_id,
                sender,
                recipient,
                subject,
                received_at,
                raw_email,
                fingerprint
            )
        )

        return {
            "status": "stored",
            "email_id": cursor.lastrowid,
            "sender": sender,
            "subject": subject,
            "sha256": fingerprint
        }
