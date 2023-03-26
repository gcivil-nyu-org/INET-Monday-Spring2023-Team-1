def validate_password(password):
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one digit.")
    if not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter.")
    if not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter.")
    if not any(char in "!@#$%^&*()-+" for char in password):
        errors.append("Password must contain at least one special character.")
    return errors