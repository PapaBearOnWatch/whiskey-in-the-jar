from intelligence.pattern_analysis import (
    analyze_domain_patterns,
    identify_email_clusters,
    generate_cluster_reports
)

domain = "example.invalid"

comparisons = analyze_domain_patterns(domain)
clusters = identify_email_clusters(comparisons)
reports = generate_cluster_reports(domain, clusters, comparisons)

print("\nCLUSTER REPORTS")
print("================")

for report in reports:
    print(f"\nCluster: {report['cluster_id']}")
    print(f"Domain: {report['domain']}")
    print(f"Messages: {report['message_count']}")

    print("\nSenders:")
    for sender in report["senders"]:
        print(f"  - {sender}")

    print("\nSubjects:")
    for subject in report["subjects"]:
        print(f"  - {subject}")

    print("\nTimestamps:")
    for timestamp in report["timestamps"]:
        print(f"  - {timestamp}")

    print(f"\nRisk levels: {report['risk_levels']}")
    print(f"Shared protocols: {report['shared_protocols']}")
    print(f"Shared hosts: {report['shared_hosts']}")
    print(f"Shared paths: {report['shared_paths']}")
    print(f"Identical URLs: {report['identical_urls']}")
    print(f"URL relationships: {report['url_relationships']}")
    print(
        "Average subject similarity: "
        f"{report['average_subject_similarity']}"
    )
    print(f"Minimum subject similarity: {report['minimum_subject_similarity']}")
    print(f"Qualifying pairs: {report['qualifying_pair_count']}")
    print(f"Possible pairs: {report['possible_pair_count']}")
    print(f"Pair coverage: {report['pair_coverage_percent']}%")
    print(f"Grouping basis: {report['grouping_basis']}")
    print(f"Caveat: {report['caveat']}")
