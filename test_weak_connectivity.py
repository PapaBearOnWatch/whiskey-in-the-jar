from intelligence.pattern_analysis import identify_email_clusters

comparisons = [
    {
        "email_ids": [101, 102],
        "different_senders": True,
        "minutes_apart": 15,
        "subject_similarity": 0.80
    },
    {
        "email_ids": [102, 103],
        "different_senders": True,
        "minutes_apart": 20,
        "subject_similarity": 0.70
    },
    {
        "email_ids": [101, 103],
        "different_senders": True,
        "minutes_apart": 35,
        "subject_similarity": 0.20
    }
]

clusters = identify_email_clusters(comparisons)

print("WEAK-CONNECTIVITY TEST")
print("======================")
print(f"Clusters identified: {clusters}")

qualifying_pairs = sum(
    comparison["different_senders"]
    and comparison["minutes_apart"] is not None
    and comparison["minutes_apart"] <= 60
    and comparison["subject_similarity"] >= 0.5
    for comparison in comparisons
)

possible_pairs = 3
coverage = qualifying_pairs / possible_pairs * 100

print(f"Qualifying pairs: {qualifying_pairs}")
print(f"Possible pairs: {possible_pairs}")
print(f"Pair coverage: {coverage:.1f}%")
