import re


def name_validator(name):
    if re.match(r'^([A-Za-z]+)( [A-Za-z]+)*( [A-Za-z]+)*$', name):
        if 2 < len(name) <= 45:
            return True
    else:
        return False


def password_validator(password):
    if re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$', password):
        if 8 <= len(password) <= 16:
            return True
    else:
        return False


def email_validator(email):
    if re.match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
        username = email.split('@')[0]
        domain = email.split('@')[1]
        domain_name = domain.split('.')[0]
        domain_type = domain.split('.')[1]
        if 3 <= len(username) <= 64:
            if 1 <= len(domain_name) <= 30:
                if 1 <= len(domain_type) <= 5:
                    return True
    else:
        return False


def number_validation(mobile_number):
    if (re.match(r'^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$', mobile_number) and
            len(mobile_number) == 10):
        return True
    else:
        return False


def title_validator(title):
    if 5 <= len(title) <= 80:
        return True
    else:
        return False

def description_validator(description):
    if len(description) <= 1000:
        return True
    else:
        return False

