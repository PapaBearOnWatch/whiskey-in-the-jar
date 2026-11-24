from intelligence.pattern_analysis import (
    analyze_domain_patterns,
    identify_email_clusters
)

comparisons = analyze_domain_patterns("example.invalid")
clusters = identify_email_clusters(comparisons)

print("\nEMAIL CLUSTERS")
print("--------------")

if clusters:
    for number, cluster in enumerate(clusters, start=1):
        print(f"Cluster {number}: Emails {cluster}")
else:
    print("No qualifying clusters identified.")
