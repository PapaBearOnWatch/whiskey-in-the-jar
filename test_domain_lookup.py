from intelligence.domain_lookup import lookup_domain

result = lookup_domain("example.invalid")

print("\nWHISKEY IN THE JAR - DOMAIN INTELLIGENCE")
print("=" * 55)

print(f"Domain: {result['domain']}")
print(f"Associated emails: {result['email_count']}")
print(f"Distinct senders: {result['distinct_senders']}")
print(f"Sender names: {', '.join(result['sender_names'])}")
print(f"Highest risk: {result['highest_risk']}")
print(f"Highest risk score: {result['highest_risk_score']}")
print(f"Lowest risk score: {result['lowest_risk_score']}")
print(f"First observed: {result['first_seen']}")
print(f"Last observed: {result['last_seen']}")
print(f"Indicator types: {', '.join(result['indicator_types'])}")

print("\nRELATIONSHIP ASSESSMENT")
print("-" * 55)
print(result["relationship"]["status"])
print(result["relationship"]["observation"])
print(result["relationship"]["assessment"])
print(result["relationship"]["caveat"])

print("\nASSOCIATED EMAILS")
print("-" * 55)

for email in result["emails"]:
    print(f"Email ID: {email['id']}")
    print(f"Sender: {email['sender']}")
    print(f"Subject: {email['subject']}")
    print(f"Risk: {email['risk_level']}")
    print(f"Score: {email['risk_score']}")
    print("-" * 35)
