from intelligence.pattern_analysis import analyze_domain_patterns
from intelligence.relationship_assessment import assess_relationship

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
