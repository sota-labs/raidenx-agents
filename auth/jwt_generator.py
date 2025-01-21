import jwt
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

def get_jwt(userId: str, userName: str, displayName: str) -> str:    
    current_time = datetime.now(timezone.utc)
    
    payload = {
        "userId": userId,
        "userName": userName,
        "displayName": displayName,
        "iap": None,
        "iat": int(current_time.timestamp()),
        "exp": int((current_time.timestamp() + (30 * 24 * 60 * 60)))
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return token


# print(get_jwt("6409124772", "hungdv", "hungdv"))