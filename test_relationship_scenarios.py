from collector.email_ingest import ingest_email
from analyzer.email_analyzer import analyze_email
from intelligence.pattern_analysis import analyze_domain_patterns
from intelligence.relationship_assessment import assess_relationship

test_emails = [
    """From: Account Support <support1@example.invalid>
To: customer@example.com
Date: Sat, 21 Nov 2026 11:00:00 -0600
Message-ID: <whiskey-test-01@example.invalid>
Subject: Account verification required

Your account verification is required.
Please review your account:
http://example.invalid/verify
""",
    """From: Account Services <support2@example.invalid>
To: customer@example.com
Date: Sat, 21 Nov 2026 11:15:00 -0600
Message-ID: <whiskey-test-02@example.invalid>
Subject: Required account verification

Account verification is required.
Please review your account:
http://example.invalid/confirm
""",
    """From: Customer Support <support3@example.invalid>
To: customer@example.com
Date: Sat, 21 Nov 2026 11:30:00 -0600
Message-ID: <whiskey-test-03@example.invalid>
Subject: Account verification required

Your account verification is required.
Please review your account:
http://example.invalid/review
"""
]

for raw_email in test_emails:
    result = ingest_email(raw_email)
    print(f"Ingestion: {result['status']}")

    if result["status"] == "stored":
        analysis = analyze_email(result["email_id"])
        print(
            f"Analyzed email {result['email_id']}: "
            f"{analysis['risk_level']}"
        )

comparisons = analyze_domain_patterns("example.invalid")
assessment = assess_relationship(comparisons)

print("\nRELATIONSHIP ASSESSMENT")
print("-----------------------")
print(f"Classification: {assessment['classification']}")
print(f"Explanation: {assessment['explanation']}")

print("\nEvidence:")
for item in assessment["evidence"]:
    print(f"- {item}")

print(f"\nCaveat: {assessment['caveat']}")
