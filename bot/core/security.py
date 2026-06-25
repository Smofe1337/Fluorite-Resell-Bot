from passlib.context import CryptContext

class PasswordManager:
    def __init__(self):
        self._pwd = CryptContext(schemes='bcrypt')


    def password_to_hash(self, password: str) -> str:
        return self._pwd.hash(password)


    def verif(self, password: str, hash: str) -> bool:
        return self._pwd.verify(password, hash)
