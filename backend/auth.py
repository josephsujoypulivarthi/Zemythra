from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dummy DB (replace later with real DB)
fake_users_db = {
    "patient": {"password": pwd_context.hash("1234"), "role": "patient"},
    "doctor": {"password": pwd_context.hash("1234"), "role": "doctor"},
    "admin": {"password": pwd_context.hash("1234"), "role": "admin"},
}

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def authenticate_user(username, password):
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["password"]):
        return None
    return {"username": username, "role": user["role"]}

def create_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)