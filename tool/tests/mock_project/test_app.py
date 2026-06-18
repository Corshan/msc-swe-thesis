from app import Auth, Database

def test_login():
    db = Database()
    auth = Auth(db)
    assert auth.login("admin", "pwd") == True

def test_logout():
    db = Database()
    auth = Auth(db)
    assert auth.logout() == True
