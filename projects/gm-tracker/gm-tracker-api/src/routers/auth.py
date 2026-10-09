import base64
import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, status

from src.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse

auth_router = APIRouter(prefix="/auth", tags=["auth"])
USERS: dict[int, UserResponse] = {}
USER_PASSWORDS: dict[str, str] = {}
_next_user_id = 1


def _token_payload(user_id: int, email: str) -> str:
    payload = {"sub": user_id, "email": email, "exp": (datetime.utcnow() + timedelta(days=7)).isoformat()}
    raw = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    return f"eyJ{raw}"


def _decode_token(token: str) -> dict:
    if not token or not token.startswith("eyJ"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        padded = token[3:] + "=" * ((4 - len(token[3:]) % 4) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode()).decode())
        return payload
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def _get_current_user(authorization: str | None = Header(default=None, alias="Authorization")) -> UserResponse:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    payload = _decode_token(authorization.replace("Bearer ", "", 1))
    user_id = payload.get("sub")
    user = USERS.get(int(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate) -> UserResponse:
    global _next_user_id

    if any(user.email == payload.email for user in USERS.values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    created = UserResponse(
        id=_next_user_id,
        name=payload.name,
        email=payload.email,
        created_at=datetime.utcnow(),
    )
    USERS[created.id] = created
    USER_PASSWORDS[payload.email] = payload.password
    _next_user_id += 1
    return created


@auth_router.post("/login", response_model=TokenResponse)
async def login_user(payload: LoginRequest) -> TokenResponse:
    user = next((item for item in USERS.values() if item.email == payload.email), None)
    if user is None or USER_PASSWORDS.get(str(payload.email)) != payload.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=_token_payload(user.id, str(user.email)), token_type="bearer")


@auth_router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: UserResponse = Depends(_get_current_user)) -> UserResponse:
    return current_user
