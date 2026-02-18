
VOWELS = {'a', 'e', 'i', 'o', 'u'}

def _is_vowel(word: str, pos: int) -> bool:
    c = word[pos].lower()
    if c in VOWELS:
        return True
    if c == "y" and pos > 0:
        return _is_consonant(word, pos - 1)
    return False


def _is_consonant(word: str, pos: int) -> bool:
    return not _is_vowel(word, pos)


def _measure(word: str) -> int:
    if not word:
        return 0
    m = 0
    i = 0
    
    while i < len(word) and _is_consonant(word, i):
        i += 1
    while i < len(word):
        while i < len(word) and _is_vowel(word, i):
            i += 1
        if i >= len(word):
            break
        m += 1
        
        while i < len(word) and _is_consonant(word, i):
            i += 1
    return m


def _contains_vowel(word: str) -> bool:
    for i in range(len(word)):
        if _is_vowel(word, i):
            return True
    return False


def _step1a(word: str) -> str:
    if not word:
        return word
    w = word.lower()

    if w.endswith("sses"):
        return w[:-4] + "ss"

    if w.endswith("ies") or w.endswith("ied"):
        stem = w[:-3]
        return stem + ("i" if len(stem) > 1 else "ie")

    if w.endswith("us") or w.endswith("ss"):
        return w

    # delete final s if preceding part contains a vowel not immediately before the s
    if w.endswith("s"):
        stem = w[:-1]
        if not _contains_vowel(stem):
            return w

        # vowel must not be immediately before the deleted s
        if len(stem) > 0 and _is_vowel(stem, len(stem) - 1):
            return w 
        return stem

    return w


def _step1b(word: str) -> str:
    """Step 1b: eed/eedly and ed/edly/ing/ingly. Longest applicable suffix."""
    if not word:
        return word
    w = word

    if w.endswith("eedly"):
        stem = w[:-5]
        if _measure(stem) > 0:
            return stem + "ee"

    elif w.endswith("eed"):
        stem = w[:-3]
        if _measure(stem) > 0:
            return stem + "ee"
        return w 

    for suffix in ("ingly", "edly", "ing", "ed"):
        if w.endswith(suffix):
            stem = w[: -len(suffix)]
            if not _contains_vowel(stem):
                return w
            
            if not stem:
                return stem
                
            if stem.endswith("at") or stem.endswith("bl") or stem.endswith("iz"):
                return stem + "e"
            
            
            if len(stem) >= 2 and stem[-1] == stem[-2]:
                if stem[-1] not in ("l", "s", "z"):
                    return stem[:-1]
            
            if _measure(stem) == 0 or len(stem) <= 3:
                return stem + "e"
            return stem

    return w


def porter_stemmer(word: str) -> str:
    if not word or not word.isalpha():
        return word
    w = _step1a(word)
    w = _step1b(w)
    return w


if __name__ == "__main__":
    # test cases
    # step 1a
    assert porter_stemmer("stresses") == "stress"
    assert porter_stemmer("gaps") == "gap"
    assert porter_stemmer("gas") == "gas"
    assert porter_stemmer("cries") == "cri"
    assert porter_stemmer("ties") == "tie"
    assert porter_stemmer("stress") == "stress"
    assert porter_stemmer("cats") == "cat"
    # step 1b
    assert porter_stemmer("agreed") == "agree"
    assert porter_stemmer("feed") == "feed"
    assert porter_stemmer("pirating") == "pirate"
    assert porter_stemmer("falling") == "fall"
    assert porter_stemmer("dripping") == "drip"
    assert porter_stemmer("hoping") == "hope"
    assert porter_stemmer("fished") == "fish"
    assert porter_stemmer("feedly") == "fee"
    assert porter_stemmer("agreedly") == "agree"
    
    print("All porter_stemmer tests passed.")
