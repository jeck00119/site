import secrets

from passlib.context import CryptContext

from repo.repositories import UsersRepository
from src.metaclasses.singleton import Singleton


class AuthService(metaclass=Singleton):
    def __init__(self):
        self.users_repository = UsersRepository()
        self.secret_key = None
        self.generate_secret()

        self.bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def get_secret(self):
        return self.secret_key

    def generate_secret(self):
        self.secret_key = secrets.token_urlsafe(32)

    def is_authenticated(self, username, password):
        user = self.users_repository.get_by_username(username)
        if user:
            if self.bcrypt_context.verify(password, user["password"]):
                return True, user
        return False, None

    def hash_password(self, password: str):
        return self.bcrypt_context.hash(password)
