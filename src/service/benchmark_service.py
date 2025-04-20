def match_to_benchmark_topic(text, benchmark_topics):
    """
    Matches a given text snippet to the most relevant ESG benchmark topic.

    Parameters:
    text (str): The input text to analyze.
    benchmark_topics (list of str): List of benchmark topic keywords or phrases.

    Returns:
    str: The first matched benchmark topic if found; otherwise, "Unaligned".
    """
    text = text.lower()
    matches = [topic for topic in benchmark_topics if topic in text]
    return matches[0] if matches else "Unaligned"


def detect_greenwashing_advanced(row, benchmark_topics):
    """
    Detects potential greenwashing in a given text snippet using multiple heuristic rules.

    Criteria for flagging as potential greenwashing:
    - Sentiment is highly positive (score > 0.85).
    - Contains ESG-related buzzwords (e.g., 'sustainable', 'net zero').
    - No numerical evidence/metrics in the statement.
    - Mentions a valid ESG benchmark topic.

    Parameters:
    row (pd.Series): A row of a DataFrame containing 'Text Snippet', 'Sentiment Label', and 'Sentiment Score'.
    benchmark_topics (list of str): List of ESG benchmark topics to validate alignment.

    Returns:
    tuple: ("Potential"/"No", matched_topic)
           - "Potential" if criteria for greenwashing is met.
           - "No" otherwise.
    """
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