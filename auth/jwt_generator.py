import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

def get_jwt(userId: str, userName: str, displayName: str) -> str:
    
    now = datetime.datetime.utcnow()
    
    exp = now + datetime.timedelta(days=30)
    
    payload = {
        "userId": userId,
        "userName": userName,
        "displayName": displayName,
        "iap": None,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return token