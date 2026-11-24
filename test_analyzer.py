from analyzer.email_analyzer import analyze_email

result = analyze_email(2)

print("\nWHISKEY IN THE JAR - EMAIL ANALYSIS")
print("=" * 50)

print(f"Email ID: {result['email_id']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Risk Score: {result['score']}")
print(f"URLs Found: {result['url_count']}")

print("\nFINDINGS")
print("-" * 50)

if result["findings"]:
    for finding in result["findings"]:
        print(f"[!] {finding['type']}")
        print(f"    {finding['description']}")
else:
    print("No suspicious indicators identified.")

print("\nASSESSMENT")
print(result["assessment"])
