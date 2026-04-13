def continued_fraction_encode(x, max_terms=20):
    """Encode a number as a continued fraction."""
    terms = []
    for _ in range(max_terms):
        a = int(x)
        terms.append(a)
        x -= a
        if x < 1e-9:
            break
        x = 1 / x
    return terms

def continued_fraction_decode(terms):
    """Decode a continued fraction to a number."""
    x = 0.0
    for term in reversed(terms):
        x = 1 / (term + x)
    return x
