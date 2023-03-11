from passlib.context import CryptContext
import re
import jwt
from dotenv import dotenv_values
from models import User
from fastapi import HTTPException, status

config_credentials = dotenv_values(".env")

# Authenticate crypted password
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# Check if password is valid, if so crypt it and return
def authenticate_password(password):
    valid_password_pattern = r'^(?=.*?[a-z])(?=.*?[0-9]).{5,}$'

    if re.fullmatch(valid_password_pattern, password):
        return pwd_context.hash(password)
    else:
        raise HTTPException(status_code=400, detail="Password needs to be at least 5 char long, at least 1 number, at least 1 letter.")



# Check if email is valid
def check_is_email_valid(email):
    email_valid_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if re.fullmatch(email_valid_regex, email):
        return email
    else:
        raise HTTPException(status_code=400, detail="Email adress is not valid.")


# Verify token
async def verify_token(token: str):
    try:
        payload = jwt.decode(token, config_credentials)
        # its a dict, we get the token depending on user key
        user = await User.get(id = payload.get("id"))

    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user