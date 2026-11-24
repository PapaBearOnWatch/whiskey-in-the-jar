from intelligence.pattern_analysis import compare_url_destinations

urls_a = [
    "http://example.invalid/verify"
]

urls_b = [
    "http://example.invalid/confirm"
]

result = compare_url_destinations(urls_a, urls_b)

print("URL DESTINATION COMPARISON")
print("--------------------------")
print(result)
