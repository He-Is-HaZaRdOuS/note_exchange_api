from string import ascii_letters, digits


def password_is_valid(password):
    if len(password) < 8:
        return False
    if not any(ele.isupper() for ele in password):
        return False
    if not any(ele.islower() for ele in password):
        return False
    if not any(ele.isdigit() for ele in password):
        return False
    if not set(password).difference(ascii_letters + digits):
        return False
    return True

def username_is_valid(username):
    if not(4 <= len(username) <= 12):
        return False
    if not username.isalnum():
        return False
    if username.lower() != username:
        return False
    return True
