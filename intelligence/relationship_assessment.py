def assess_relationship(comparisons):
    if not comparisons:
        return {
            "classification": "LIMITED",
            "explanation": "There are not enough email comparisons to assess a relationship.",
            "evidence": [],
            "caveat": "No observed relationship does not establish that a domain is safe."
        }

    all_email_ids = set()
    qualifying_pairs = set()
    close_pairs = set()
    similar_subject_pairs = set()
    shared_protocols = set()

    for comparison in comparisons:
        email_ids = comparison["email_ids"]
        all_email_ids.update(email_ids)

        pair = tuple(sorted(email_ids))

        minutes = comparison["minutes_apart"]
        similarity = comparison["subject_similarity"]

        if (
            comparison["different_senders"]
            and minutes is not None
            and minutes <= 60
            and similarity >= 0.5
        ):
            qualifying_pairs.add(pair)

        if minutes is not None and minutes <= 60:
            close_pairs.add(pair)

        if similarity >= 0.5:
            similar_subject_pairs.add(pair)

        shared_protocols.update(comparison["shared_protocols"])

    evidence = []

    evidence.append(
        f"{len(all_email_ids)} distinct emails were included in the comparisons."
    )

    if close_pairs:
        evidence.append(
            f"{len(close_pairs)} unique email pairs were observed within 60 minutes."
        )

    if similar_subject_pairs:
        evidence.append(
            f"{len(similar_subject_pairs)} unique email pairs showed subject similarity of 0.50 or greater."
        )

    if qualifying_pairs:
        evidence.append(
            f"{len(qualifying_pairs)} unique pairs combined different senders, close timing, and similar subjects."
        )

    if shared_protocols:
        evidence.append(
            "Shared URL protocols were observed: "
            + ", ".join(sorted(shared_protocols))
            + ". Protocol similarity is weak supporting evidence."
        )

    if len(all_email_ids) >= 3 and len(qualifying_pairs) >= 2:
        classification = "MODERATE"
        explanation = (
            "Multiple distinct emails show recurring similarities across "
            "sender identity, timing, and subject wording. This pattern "
            "warrants further investigation, but does not establish a campaign."
        )
    else:
        classification = "LIMITED"
        explanation = (
            "The observed similarities are currently weak or insufficient "
            "to support a stronger relationship assessment."
        )

    return {
        "classification": classification,
        "explanation": explanation,
        "evidence": evidence,
        "caveat": (
            "This is a heuristic assessment, not a probability or proof of "
            "common ownership, coordination, or campaign activity. Pairwise "
            "comparisons are related observations, not independent evidence."
        )
    }
def assess_cluster(cluster_report):
    from email.utils import parsedate_to_datetime

    message_count = cluster_report["message_count"]
    sender_count = len(cluster_report["senders"])
    similarity = cluster_report["average_subject_similarity"]

    timestamps = []

    for value in cluster_report["timestamps"]:
        if not value:
            continue

        try:
            timestamps.append(parsedate_to_datetime(value))
        except (TypeError, ValueError, OverflowError):
            continue

    time_span_minutes = None

    if len(timestamps) >= 2:
        time_span_minutes = (
            max(timestamps) - min(timestamps)
        ).total_seconds() / 60

    risk_levels = cluster_report["risk_levels"]

    risk_summary = {
        "HIGH": risk_levels.count("HIGH"),
        "MEDIUM": risk_levels.count("MEDIUM"),
        "LOW": risk_levels.count("LOW"),
        "UNKNOWN": risk_levels.count(None)
    }

    evidence = [
        f"{message_count} messages are in this cluster.",
        f"{sender_count} distinct sender entries were observed."
    ]

    if similarity is not None:
        evidence.append(f"Average subject similarity: {similarity:.2f}.")

    if time_span_minutes is not None:
        evidence.append(f"Messages span {time_span_minutes:.1f} minutes.")

    evidence.append(f"Individual risk levels: {risk_summary}.")

    if cluster_report["shared_protocols"]:
        evidence.append(
            "Shared URL protocols: "
            + ", ".join(cluster_report["shared_protocols"])
            + ". This is weak supporting evidence."
        )

    if (
        message_count >= 3
        and sender_count >= 3
        and similarity is not None
        and similarity >= 0.5
        and time_span_minutes is not None
        and time_span_minutes <= 60
    ):
        classification = "NOTABLE PATTERN"
        explanation = (
            "Multiple messages from distinct senders show similar subject "
            "wording within a concentrated time period. Further investigation "
            "is warranted."
        )
    else:
        classification = "LIMITED PATTERN"
        explanation = (
            "The available cluster characteristics do not establish a "
            "particularly strong recurring pattern."
        )

    return {
        "classification": classification,
        "explanation": explanation,
        "time_span_minutes": (
            round(time_span_minutes, 1)
            if time_span_minutes is not None else None
        ),
        "risk_summary": risk_summary,
        "evidence": evidence,
        "caveat": (
            "This assessment describes a pattern across messages. "
            "It does not establish malicious intent, common ownership, "
            "coordination, or campaign activity. Individual message "
            "risk assessments remain separate."
        )
    }
