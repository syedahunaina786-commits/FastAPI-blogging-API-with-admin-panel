from fastapi import APIRouter, HTTPException, status
from app.schemas import UserRegister, UserLogin, TokenResponse
from app.database import users_collection
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_doc = {
        "username": user.username,
        "email": user.email,
        "password": hash_password(user.password),
        "is_admin": True
    }
    result = await users_collection.insert_one(user_doc)
    return {
        "message": "User registered successfully",
        "id": str(result.inserted_id),
        "username": user.username,
        "email": user.email
    }


@router.post("/login", response_model=TokenResponse)
async def login_user(credentials: UserLogin):
    user = await users_collection.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token({"sub": user["email"], "username": user["username"]})
    return {"access_token": token, "token_type": "bearer"}
