import jwt
import datetime as dt
from backend.config import JWT_KEY
from backend import models
from backend.logic import crud
from backend.logic.db import sql
from pwdlib import PasswordHash
from backend.logic import errors
hasher = PasswordHash.recommended()

def create_access_token(user_id: int, exp: dt.datetime) -> str:
    payload = {
        'sub': str(user_id),
        'exp': exp
    }

    return jwt.encode(
        payload,
        key = JWT_KEY,
        algorithm = 'HS256'
    )


def verify_access_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, key = JWT_KEY, algorithms = ['HS256'])
    except:
        raise errors.AuthenticationError('Invalid token')
    return payload



def signup(user: models.UserInput) -> str | None:
    user = crud.add_user(user)
    token = create_access_token(
        user_id = user.id, 
        exp = dt.datetime.now(dt.UTC) + dt.timedelta(days = 30)
    )
    return token


def login(user: models.LoginUser) -> str | None:
    # get stored user
    user_in_db = crud.get_user(email = user.email)
    # verify password
    if not hasher.verify(user.password, user_in_db.password_hash):
        raise errors.AuthenticationError('Invalid password')

    # issue token
    token = create_access_token(
        user_in_db.id, 
        dt.datetime.now(dt.UTC) + dt.timedelta(days = 30)
    )
    return token

def get_current_user(token: str) -> models.User | None:
    user_data = verify_access_token(token)
    return crud.get_user(id = int(user_data['sub']))
