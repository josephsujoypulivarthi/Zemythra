# backend/auth.py
import jwt 
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from passlib.context import CryptContext

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Path to users database
USERS_DB_FILE = "backend/users.json"
SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"


def load_users() -> Dict:
    """Load users from JSON file"""
    if os.path.exists(USERS_DB_FILE):
        with open(USERS_DB_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users: Dict):
    """Save users to JSON file"""
    with open(USERS_DB_FILE, "w") as f:
        json.dump(users, f, indent=2)


def hash_password(password: str) -> str:
    """Hash a plain text password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain text password against hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> bool:
    """
    Authenticate user credentials against database
    """
    users = load_users()
    
    if username not in users:
        return False
    
    user = users[username]
    return verify_password(password, user["hashed_password"])


def create_user(username: str, password: str, role: str = "user", email: str = "") -> bool:
    """
    Create new user with hashed password
    """
    users = load_users()
    
    if username in users:
        return False  # User already exists
    
    users[username] = {
        "hashed_password": hash_password(password),
        "role": role,
        "email": email,
        "created_at": datetime.now().isoformat()
    }
    
    save_users(users)
    return True


def delete_user(username: str) -> bool:
    """Delete user from database"""
    users = load_users()
    
    if username not in users:
        return False
    
    del users[username]
    save_users(users)
    return True


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token for authenticated user"""
    import jwt
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    
    try:
        import jwt
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except:
        return f"token_{to_encode.get('sub', 'user')}"


def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        return None


def list_all_users() -> Dict:
    """List all users (without showing hashed passwords)"""
    users = load_users()
    safe_users = {}
    for username, data in users.items():
        safe_users[username] = {
            "role": data.get("role"),
            "email": data.get("email"),
            "created_at": data.get("created_at")
        }
    return safe_users