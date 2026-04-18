# backend/auth.py - COMPLETE FIXED VERSION
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from passlib.context import CryptContext
import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS_DB_FILE = "backend/users.json"
SECRET_KEY = "aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4yZ5"
ALGORITHM = "HS256"


def ensure_users_file_exists():
    """✅ FIX #1: Auto-create and recover corrupted files"""
    try:
        if not os.path.exists(USERS_DB_FILE):
            print(f"📝 Creating {USERS_DB_FILE}...")
            os.makedirs(os.path.dirname(USERS_DB_FILE), exist_ok=True)
            with open(USERS_DB_FILE, 'w') as f:
                json.dump({}, f)
            print(f"✅ Created {USERS_DB_FILE}")
            return
        
        # Check if file is valid JSON
        with open(USERS_DB_FILE, 'r') as f:
            content = f.read().strip()
            
            if not content:  # Empty file
                print(f"⚠️ {USERS_DB_FILE} is empty, fixing...")
                with open(USERS_DB_FILE, 'w') as fw:
                    json.dump({}, fw)
                print(f"✅ Fixed {USERS_DB_FILE}")
            else:
                # Try to parse JSON
                try:
                    json.loads(content)
                    print(f"✅ {USERS_DB_FILE} is valid")
                except json.JSONDecodeError:
                    print(f"⚠️ {USERS_DB_FILE} corrupted, recreating...")
                    with open(USERS_DB_FILE, 'w') as fw:
                        json.dump({}, fw)
                    print(f"✅ Recreated {USERS_DB_FILE}")
    except Exception as e:
        print(f"❌ Error in ensure_users_file_exists: {e}")


def load_users() -> Dict:
    """✅ FIX #2: Load with automatic recovery"""
    ensure_users_file_exists()
    
    try:
        with open(USERS_DB_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return {}
            data = json.loads(content)
            print(f"✅ Loaded {len(data)} users from file")
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ Error loading users: {e}, returning empty dict")
        return {}


def save_users(users: Dict):
    """✅ FIX #3: Save with verification"""
    try:
        ensure_users_file_exists()
        
        # Make sure directory exists
        os.makedirs(os.path.dirname(USERS_DB_FILE) or '.', exist_ok=True)
        
        # Write to file
        with open(USERS_DB_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        
        print(f"✅ Saved {len(users)} users to {USERS_DB_FILE}")
        
        # Verify it was saved
        with open(USERS_DB_FILE, 'r') as f:
            verify = json.load(f)
            print(f"✅ Verified: {len(verify)} users in file")
            
    except Exception as e:
        print(f"❌ Error saving users: {e}")
        raise


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    try:
        hashed = pwd_context.hash(password)
        print(f"✅ Password hashed successfully")
        return hashed
    except Exception as e:
        print(f"❌ Error hashing password: {e}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"❌ Error verifying password: {e}")
        return False


def authenticate_user(username: str, password: str) -> bool:
    """✅ FIX #4: Authenticate with debug info"""
    print(f"🔐 Attempting to authenticate: {username}")
    
    users = load_users()
    
    if username not in users:
        print(f"❌ User {username} not found")
        return False
    
    user = users[username]
    is_valid = verify_password(password, user.get("password", ""))
    
    if is_valid:
        print(f"✅ User {username} authenticated successfully")
    else:
        print(f"❌ Invalid password for {username}")
    
    return is_valid


def create_user(username: str, password: str, role: str = "user", email: str = "") -> bool:
    """✅ FIX #5: Create user with full logging"""
    print(f"\n{'='*60}")
    print(f"🆕 CREATING NEW USER: {username}")
    print(f"{'='*60}")
    
    try:
        # Step 1: Load existing users
        print(f"1️⃣ Loading existing users...")
        users = load_users()
        print(f"   Found {len(users)} existing users")
        
        # Step 2: Check if username exists
        print(f"2️⃣ Checking if username exists...")
        if username in users:
            print(f"   ❌ Username '{username}' already exists!")
            return False
        print(f"   ✅ Username available")
        
        # Step 3: Hash password
        print(f"3️⃣ Hashing password...")
        hashed_pwd = hash_password(password)
        
        # Step 4: Create user object
        print(f"4️⃣ Creating user object...")
        user_data = {
            "password": hashed_pwd,
            "role": role,
            "email": email,
            "created_at": datetime.now().isoformat()
        }
        print(f"   User data prepared: {list(user_data.keys())}")
        
        # Step 5: Add to users dict
        print(f"5️⃣ Adding to users dictionary...")
        users[username] = user_data
        print(f"   Total users now: {len(users)}")
        
        # Step 6: Save to file
        print(f"6️⃣ Saving to users.json...")
        save_users(users)
        
        # Step 7: Verify
        print(f"7️⃣ Verifying save...")
        verify_users = load_users()
        if username in verify_users:
            print(f"   ✅ Verified: {username} is in file")
        else:
            print(f"   ❌ ERROR: {username} NOT in file after save!")
            return False
        
        print(f"{'='*60}")
        print(f"✅ USER CREATED SUCCESSFULLY: {username}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR CREATING USER: {e}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()
        return False


def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """✅ FIX #6: Create JWT token with error handling"""
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        print(f"✅ JWT token created for user: {data.get('sub')}")
        return encoded_jwt
        
    except Exception as e:
        print(f"❌ Error creating token: {e}")
        raise