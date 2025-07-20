import re
from better_profanity import profanity

profanity.load_censor_words()

PROFANE_WORDS = sorted((str(word) for word in profanity.CENSOR_WORDSET), key=len, reverse=True)

def normalize(text):
    """Return a lowercase string with only letters, no symbols/spaces."""
    return re.sub(r'[^a-zA-Z]', '', str(text)).lower()

def smart_censor(text):
    text_str = str(text)
    normalized = normalize(text_str)

    normalized_to_original = []
    original_idx = 0
    for char in text_str:
        if char.isalpha():
            normalized_to_original.append(original_idx)
        original_idx += 1

    censor_mask = [False] * len(text_str)

    for bad_word in PROFANE_WORDS:
        bad_word = bad_word.lower()

        for match in re.finditer(re.escape(bad_word), normalized):
            start, end = match.start(), match.end()

            for norm_idx in range(start, end):
                orig_idx = normalized_to_original[norm_idx]
                censor_mask[orig_idx] = True

    censored_chars = [
        '*' if censor_mask[i] else text_str[i]
        for i in range(len(text_str))
    ]

    return ''.join(censored_chars)
