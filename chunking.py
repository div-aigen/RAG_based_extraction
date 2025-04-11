def sentence_chunking(text: str, max_tokens: int):
    # Split into sentences first (handling common sentence endings)
    sentences = []
    current_sentence = []

    # Split into words but preserve punctuation
    words = text.split()

    for word in words:
        current_sentence.append(word)
        # Check for sentence endings (.!?)
        if word.endswith(('.', '!', '?')):
            sentences.append(' '.join(current_sentence))
            current_sentence = []

    # Handle any remaining text as a sentence
    if current_sentence:
        sentences.append(' '.join(current_sentence))

    # Now create chunks from complete sentences
    chunks = []
    current_chunk = []
    current_tokens = 0

    for sentence in sentences:
        sentence_tokens = len(sentence.split())

        # If adding this sentence would exceed max_tokens
        if current_tokens + sentence_tokens > max_tokens:
            if current_chunk:  # Save current chunk if it exists
                chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_tokens = sentence_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

    # Add the final chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
