import re


def validate_username(username):
    return bool(re.match(r"^(?![0-9])[\dA-Za-z]+$", username))


def validate_password(password):
    return bool(re.match(r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}$", password))
