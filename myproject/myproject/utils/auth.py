import jwt
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
load_dotenv()
import bcrypt


SECRET_KEY = os.environ.get('SECRET_KEY')

def create_token(user_id, username, profile_pic):
    # user_id, username, profile_pic, exp
    payload = {
        "user_id": user_id,
        "username": username,
        "profile_pic": profile_pic,
        "exp": datetime.now(pytz.utc) + timedelta(hours=5)  # Token expires in 5 hours
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def are_passwords_the_same(plain_text_password, hashed_password):
    # this would be the the retrived HASHED password from teh database. Both of them are strings and they need to be encoded to be used by bcrypt.checkpw
    hashed_password = hashed_password.encode('utf-8')

    # Compare entered password with stored hash
    if bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password):
        return True
    else:
        return False
    


def verify_token(token):
    if not token.startswith("Bearer "):
        return {"status": False, "message": "Missing or invalid token"}
    token = token.split(" ")[1]

    try:
        # user_id, username, profile_pic, exp
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = int(payload["user_id"])
        username = payload["username"]
        profile_pic = payload["profile_pic"]
        return {
            "status": True,
            "user_id": user_id,
            "username": username,
            "profile_pic": profile_pic
        }

    except jwt.ExpiredSignatureError:
        return {"status": False, "message": "Token expired"}

    except jwt.InvalidTokenError:
        return {"status": False, "message": "Invalid token"}