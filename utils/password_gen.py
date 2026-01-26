# utils/password_gen.py

import secrets
import string


UPPER = string.ascii_uppercase
LOWER = string.ascii_lowercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?"


def generate_password(
    length: int = 20,
    use_upper=True,
    use_lower=True,
    use_digits=True,
    use_symbols=True,
):
    if length < 18:
        raise ValueError("Password length must be at least 18 characters")

    pools = []
    password_chars = []

    if use_upper:
        pools.append(UPPER)
        password_chars.append(secrets.choice(UPPER))

    if use_lower:
        pools.append(LOWER)
        password_chars.append(secrets.choice(LOWER))

    if use_digits:
        pools.append(DIGITS)
        password_chars.append(secrets.choice(DIGITS))

    if use_symbols:
        pools.append(SYMBOLS)
        password_chars.append(secrets.choice(SYMBOLS))

    if not pools:
        raise ValueError("At least one character set must be enabled")

    remaining_length = length - len(password_chars)
    all_chars = "".join(pools)

    for _ in range(remaining_length):
        password_chars.append(secrets.choice(all_chars))

    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


def password_strength(pwd: str) -> str:
    score = 0

    if len(pwd) >= 18:
        score += 2
    elif len(pwd) >= 12:
        score += 1

    if any(c.islower() for c in pwd):
        score += 1
    if any(c.isupper() for c in pwd):
        score += 1
    if any(c.isdigit() for c in pwd):
        score += 1
    if any(not c.isalnum() for c in pwd):
        score += 1

    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Okay"
    elif score <= 6:
        return "Strong"
    else:
        return "Very Strong"
