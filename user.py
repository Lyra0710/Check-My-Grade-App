class User:
    def __init__(self, user_id, email_address, first_name, last_name, role):
        self.user_id = str(user_id)
        self.email_address = email_address
        self.first_name = first_name
        self.last_name = last_name
        self.role = role 