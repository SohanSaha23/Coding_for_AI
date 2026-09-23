def search4letters(phrase: str, letters: str = 'aeiou') -> set:
    """Return the set of 'letters' found in 'phrase'."""
    return set(letters).intersection(set(phrase))


def search4vowels(phrase: str) -> set:
    """Return any vowels found in a supplied phrase."""
    return search4letters(phrase, 'aeiou')
