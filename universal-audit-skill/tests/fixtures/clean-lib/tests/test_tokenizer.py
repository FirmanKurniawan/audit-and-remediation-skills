from cleanlib import tokenize, cache_key


def test_tokenize_splits_symbols():
    assert tokenize("1 + 2*3") == ["1", "+", "2", "*", "3"]


def test_tokenize_empty():
    assert tokenize("") == []


def test_cache_key_is_stable():
    assert cache_key("a", "b") == cache_key("a", "b")
    assert cache_key("a", "b") != cache_key("b", "a")
