import re
from collections import defaultdict
from heapq import nlargest # Used to find the 'n' largest values efficiently

def custom_sentence_tokenizer(text):
    """
    Splits text into sentences using basic punctuation and whitespace.
    """
    # Use regular expression to split by common sentence-ending punctuation
    # followed by whitespace or end of string.
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Filter out empty strings that might result from splitting
    return [s.strip() for s in sentences if s.strip()]

def get_word_frequencies(text):
    """
    Calculates the frequency of each non-stop word in the text.
    """
    # A very basic list of common English stop words.
    # In a real-world scenario, you'd use a more comprehensive list.
    stop_words = set([
        "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
        "can", "do", "does", "for", "from", "go", "has", "have", "he",
        "her", "him", "his", "how", "i", "if", "in", "is", "it", "its",
        "just", "me", "my", "no", "not", "of", "on", "or", "our", "out",
        "she", "so", "some", "such", "than", "that", "the", "their", "them",
        "then", "there", "these", "they", "this", "those", "to", "up",
        "us", "was", "we", "what", "when", "where", "which", "who", "whom",
        "why", "will", "with", "you", "your"
    ])

    word_frequencies = defaultdict(int)
    # Convert text to lowercase and remove non-alphabetic characters
    words = re.findall(r'\b[a-z]+\b', text.lower())

    for word in words:
        if word not in stop_words:
            word_frequencies[word] += 1
    return word_frequencies

def summarize_article_custom(article_text, num_sentences=5):
    """
    Summarizes an article using custom sentence tokenization and word frequency.

    Args:
        article_text (str): The lengthy article to be summarized.
        num_sentences (int): The desired number of sentences in the summary.

    Returns:
        str: A concise summary of the article.
    """
    if not article_text or len(article_text.strip()) == 0:
        return "Error: Input article text cannot be empty."

    # Step 1: Tokenize into sentences
    sentences = custom_sentence_tokenizer(article_text)
    if not sentences:
        return "Error: No sentences found in the input article."

    # Step 2: Calculate word frequencies across the entire article
    word_frequencies = get_word_frequencies(article_text)

    # Step 3: Score each sentence based on the frequency of its important words
    sentence_scores = defaultdict(int)
    for i, sentence in enumerate(sentences):
        # Clean the sentence for scoring (lowercase, remove non-alphabetic)
        clean_sentence_words = re.findall(r'\b[a-z]+\b', sentence.lower())
        for word in clean_sentence_words:
            if word in word_frequencies:
                sentence_scores[i] += word_frequencies[word]

    # Step 4: Select the top N sentences for the summary
    # Use nlargest to get the indices of sentences with the highest scores
    # and their corresponding scores.
    # The 'key=sentence_scores.get' makes nlargest sort by the dictionary value.
    if num_sentences > len(sentences):
        num_sentences = len(sentences) # Don't ask for more sentences than available

    # Get the indices of the top-scoring sentences
    top_sentence_indices = nlargest(num_sentences, sentence_scores, key=sentence_scores.get)

    # Reconstruct the summary in the original order of sentences
    # Sort the selected indices to maintain chronological order in the summary
    top_sentence_indices.sort()

    summary_sentences = [sentences[i] for i in top_sentence_indices]

    return " ".join(summary_sentences)

if __name__ == "__main__":
    print("Welcome to the Custom Article Summarizer Tool!")
    print("-" * 40)

    example_article = """
    Artificial intelligence (AI) is a rapidly expanding field that aims to create machines
    that can perform tasks typically requiring human intelligence. This includes learning,
    problem-solving, perception, and decision-making. Recent advancements in deep learning
    and neural networks have significantly boosted AI's capabilities, leading to breakthroughs
    in areas like image recognition, natural language processing, and autonomous vehicles.

    One of the primary drivers of AI development is the increasing availability of large
    datasets and computational power. These resources enable AI models to be trained
    on vast amounts of information, allowing them to identify complex patterns and make
    accurate predictions. The applications of AI are diverse and growing, impacting
    industries from healthcare and finance to education and entertainment.

    In healthcare, AI is being used for disease diagnosis, drug discovery, and personalized
    treatment plans. Financial institutions leverage AI for fraud detection, algorithmic
    trading, and risk assessment. Educational platforms employ AI to personalize learning
    experiences and provide intelligent tutoring systems. Even in entertainment, AI powers
    recommendation engines and generates realistic special effects.

    However, the rise of AI also presents challenges and ethical considerations. Concerns
    include job displacement due to automation, algorithmic bias, privacy issues, and the
    potential for misuse of AI technologies. Developers and policymakers are actively working
    to address these issues by promoting responsible AI development, establishing ethical
    guidelines, and ensuring transparency in AI systems. The future of AI promises
    even more transformative changes, but careful consideration of its societal impact
    will be crucial for harnessing its full potential responsibly.
    """

    print("Original Article (Example):")
    print(example_article)
    print("\n" + "=" * 40 + "\n")

    desired_sentences = 5 # You can change this number

    print(f"Generating summary with {desired_sentences} sentences...")
    summary = summarize_article_custom(example_article, desired_sentences)

    print("\n" + "=" * 40)
    print("Concise Summary:")
    print(summary)
    print("\n" + "=" * 40)
