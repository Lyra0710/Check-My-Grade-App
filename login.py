# login.py
import csv, hashlib, hmac, os

class LoginCredential:
    def __init__(self, file_path: str, iters: int = 1000):
        self.file = file_path
        self.iters = iters


    def encrypt_password(self, password, salt_hex):
        salt = bytes.fromhex(salt_hex)
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, self.iters)
        return hashed.hex()
    
    def decrypt_password(self, entered_password, salt_hex, hashed_hex):
        salt = bytes.fromhex(salt_hex)
        re_hash = hashlib.pbkdf2_hmac("sha256", entered_password.encode("utf-8"), salt, self.iters)
        return hmac.compare_digest(re_hash.hex(), hashed_hex)
        
    # It's simpler to work with json that csv. Creating helper functions for this purpose
    def csv_to_json(self, csv_file):
        with open(csv_file, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    def json_to_csv(self, json_data, csv_file):
        if not json_data:
            return
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[json_data[0].keys()])
            writer.writeheader()
            writer.writerows(json_data)
        
    def login(self,email, password):
        users = self.csv_to_json(self.file)
        if not users:
            return None
        
        for user in users:
            if user.get("Email") == email:
                stored_password = user.get("Password")
                salt_hex = user.get("Salt", "")
                role = user.get("Role")
                
                if self.decrypt_password(password, salt_hex, stored_password):
                    return role
                else:
                    return None
                
        return None
    
    def logout(self):
        return True
    def change_password(self, file, email, old_password, new_password):
        users = self.csv_to_json(file)
        if not users:
            return False
        
        for user in users:
            if user.get("Email") == email:
                stored_password = user.get("Password")
                salt_hex = user.get("Salt")
                if not (salt_hex and stored_password and self.decrypt_password(old_password, salt_hex, stored_password)):
                    return False
                new_salt_hex = os.urandom(16).hex()
                new_hash = self.encrypt_password(new_password, new_salt_hex)
                user["Password"] = new_hash
                user["Salt"] = new_salt_hex

                self.json_to_csv(users, file)

        return False
