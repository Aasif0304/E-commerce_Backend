import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Security,
    status,
)
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User
from schemas.user_schema import UserRegister, UserResponse

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Authentication"])

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY missing in .env file")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register user",
    description="Register a new user account.",
)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=password_hash.hash(user_data.password),
        role="USER",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    summary="Login user",
    description=(
        "Login using email and password. "
        "Supports both JSON request body and form data. "
        "Returns user details, role and access token."
    ),
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "example": "aasif@example.com"},
                            "password": {"type": "string", "example": "password123"},
                        },
                        "required": ["email", "password"],
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "example": "aasif@example.com"},
                            "password": {"type": "string", "example": "password123"},
                        },
                        "required": ["email", "password"],
                    }
                },
            },
        }
    },
)
async def login_user(
    request: Request,
    db: Session = Depends(get_db),
):
    email = None
    password = None

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                email = body.get("email") or body.get("username")
                password = body.get("password")
        except Exception:
            pass

    if not email or not password:
        try:
            form = await request.form()
            email = form.get("email") or form.get("username")
            password = form.get("password")
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email and password are required",
        )

    user = db.query(User).filter(
        User.email == str(email).strip()
    ).first()

    if not user or not password_hash.verify(
        str(password),
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = jwt.encode(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "exp": expire,
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return {
        "message": "Login successful",
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "access_token": access_token,
        "token_type": "bearer",
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        subject = payload.get("sub")

        if not subject:
            raise ValueError("Token subject is missing")

        user_id = int(subject)

    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user
