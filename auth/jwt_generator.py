import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

def get_jwt(userId: str, userName: str, displayName: str) -> str:
    
    # Current time
    now = datetime.datetime.utcnow()
    
    # Expiration time (1 month from now)
    exp = now + datetime.timedelta(days=30)
    
    # Payload for the JWT
    payload = {
        "userId": userId,
        "userName": userName,
        "displayName": displayName,
        "iap": None,  # `iap` is null
        "iat": int(now.timestamp()),  # Issued at
        "exp": int(exp.timestamp())   # Expiration
    }
    
    # Generate JWT
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return token


userId = "2104920255"
userName = "harrydang1"
displayName = "Harry Dang"

jwt_token = get_jwt(userId, userName, displayName)
print(jwt_token)