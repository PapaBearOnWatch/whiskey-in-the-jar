from intelligence.pattern_analysis import (
    analyze_domain_patterns,
    identify_email_clusters,
    generate_cluster_reports
)
from intelligence.relationship_assessment import assess_cluster

domain = "example.invalid"

comparisons = analyze_domain_patterns(domain)
clusters = identify_email_clusters(comparisons)
reports = generate_cluster_reports(domain, clusters, comparisons)

print("\nCLUSTER-LEVEL ASSESSMENT")
print("========================")

for report in reports:
    assessment = assess_cluster(report)

    print(f"\nCluster: {report['cluster_id']}")
    print(f"Classification: {assessment['classification']}")
    print(f"Explanation: {assessment['explanation']}")

    print("\nEvidence:")
    for item in assessment["evidence"]:
        print(f"- {item}")

    print(f"\nIndividual risk summary: {assessment['risk_summary']}")
    print(f"Caveat: {assessment['caveat']}")
