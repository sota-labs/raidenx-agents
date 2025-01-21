from fastapi import Security, HTTPException, Depends
from fastapi.security import HTTPBearer
import os
import jwt
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

reusable_oauth2 = HTTPBearer(
    scheme_name='Authorization'
)

def get_token(authorization: HTTPBearer = Depends(reusable_oauth2)):
    return authorization.credentials

def verify_token(token: str = Security(get_token)):
    payload = None
    try:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=['HS256'], verify=True)
        
        required_fields = ["userId", "userName", "displayName"]
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            raise jwt.InvalidTokenError()
            
        return payload
        
    except jwt.ExpiredSignatureError as e:
        error_response = {
            "message": "Token has expired",
            "error_key": "token_expired",
            "statusCode": 401
        }
        raise HTTPException(status_code=401, detail=error_response)
    except jwt.InvalidTokenError as e:
        error_response = {
            "message": "Invalid token",
            "error_key": "invalid_token",
            "statusCode": 401
        }
        raise HTTPException(status_code=401, detail=error_response)
    except Exception as e:
        error_response = {
            "message": str(e),
            "error_key": "token_error",
            "statusCode": 401
        }
        raise HTTPException(status_code=401, detail=error_response)
    
    