def get_first_error(errors):
    """
    if errors = {
        "email": ["Email is required."],
    }
    then list(errors.values())[0][0] = "Email is required."
    """
    return list(errors.values())[0][0]
