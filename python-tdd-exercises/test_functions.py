from functions import *


def test_is_even():
    assert is_even(4) == True


def test_get_initials():
    assert get_initials("John Smith") == "JS"


def test_count_vowels():
    assert count_vowels("hello") == 2


def test_filter_even_numbers():
    assert filter_even_numbers([1, 2, 3, 4, 5]) == [2, 4]


def test_is_palindrome():
    assert is_palindrome("level") == True

def test_find_longest_word():
    assert find_longest_word(
        ["cat", "elephant", "dog"]
    ) == "elephant"


def test_filter_odd_numbers():
    assert filter_odd_numbers(
        [1, 2, 3, 4, 5]
    ) == [1, 3, 5]


def test_calculate_discount():
    assert calculate_discount(
        100, 20
    ) == 80


def test_find_shortest_word():
    assert find_shortest_word(
        ["elephant", "cat", "giraffe"]
    ) == "cat"


def test_grade_score():
    assert grade_score(75) == "A"


def test_mask_email():
    assert mask_email(
        "john@gmail.com"
    ) == "j***@gmail.com"


def test_count_passes_and_fails():
    assert count_passes_and_fails(
        [20, 50, 80]
    ) == {
        "passes": 2,
        "fails": 1
    }


def test_count_words():
    assert count_words(
        "cat cat dog"
    ) == {
        "cat": 2,
        "dog": 1
    }
