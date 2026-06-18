class Database:
    def query(self, sql):
        return "result"

class Auth:
    def __init__(self, db):
        self.db = db
        
    def login(self, user, pwd):
        self.db.query("SELECT * FROM users")
        return True
        
    def logout(self):
        return True
