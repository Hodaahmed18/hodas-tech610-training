def is_even(number):
    if number % 2 == 0:
        return True
    else:
        return False


def get_initials(name):
    names = name.split()

    first_initial = names[0][0]
    second_initial = names[1][0]

    return first_initial + second_initial


def count_vowels(text):
    vowels = "aeiou"
    count = 0

    for letter in text.lower():
        if letter in vowels:
            count += 1

    return count


def filter_even_numbers(numbers):
    result = []

    for number in numbers:
        if number % 2 == 0:
            result.append(number)

    return result


def is_palindrome(text):
    text = text.lower()

    if text == text[::-1]:
        return True
    else:
        return False

def find_longest_word(words):
    longest = words[0]

    for word in words:
        if len(word) > len(longest):
            longest = word

    return longest


def filter_odd_numbers(numbers):
    result = []

    for number in numbers:
        if number % 2 != 0:
            result.append(number)

    return result


def calculate_discount(price, discount):
    return price - (price * discount / 100)


def find_shortest_word(words):
    shortest = words[0]

    for word in words:
        if len(word) < len(shortest):
            shortest = word

    return shortest


def grade_score(score):
    if score >= 70:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    else:
        return "Fail"


def mask_email(email):
    username, domain = email.split("@")
    return username[0] + "***@" + domain


def count_passes_and_fails(scores):
    passes = 0
    fails = 0

    for score in scores:
        if score >= 40:
            passes += 1
        else:
            fails += 1

    return {
        "passes": passes,
        "fails": fails
    }


def count_words(sentence):
    counts = {}

    words = sentence.split()

    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1

    return counts
