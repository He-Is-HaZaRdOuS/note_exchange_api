from string import ascii_letters, digits
import toml

# Load the TOML file
with open('configuration/config.toml', 'r') as file:
    config = toml.load(file)

reserved_usernames = config['users']['reserved_usernames']
elevated_usernames = config['users']['elevated_usernames']


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

def username_is_reserved(username):
    return username in reserved_usernames

def username_is_elevated(username):
    return username in elevated_usernames
