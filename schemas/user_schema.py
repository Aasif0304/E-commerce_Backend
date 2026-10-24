
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        description="Name of the user"
    )
    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="User password"
    )


class UserResponse(BaseModel):
    id: int = Field(
        ...,
        description="Unique user identifier",
        examples=[1]
    )
    name: str = Field(
        ...,
        description="Name of the user"
    )
    email: EmailStr = Field(
        ...,
        description="User email address"
    )

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str