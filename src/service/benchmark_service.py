def match_to_benchmark_topic(text, benchmark_topics):
    text = text.lower()
    matches = [topic for topic in benchmark_topics if topic in text]
    return matches[0] if matches else "Unaligned"

def detect_greenwashing_advanced(row, benchmark_topics):
    text = row['Text Snippet'].lower()
    sentiment = row['Sentiment Label'].lower()
    score = row['Sentiment Score']
    has_number = any(char.isdigit() for char in text)

    # Match benchmark
    matched_topic = match_to_benchmark_topic(text, benchmark_topics)

    # Buzzwords to look for
    buzzwords = ["green", "eco", "sustainable", "net zero", "inclusive", "carbon neutral", "ethical"]
    buzz_count = sum(1 for b in buzzwords if b in text)

    # Criteria: Positive tone, high sentiment, buzzwords, no metric, topic exists
    if sentiment == "positive" and score > 0.85 and buzz_count >= 1 and not has_number and matched_topic != "Unaligned":
        return "Potential", matched_topic
    return "No", matched_topic