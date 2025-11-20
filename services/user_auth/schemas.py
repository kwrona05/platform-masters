from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    nickname: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    confirmPassword: str = Field(min_length=8, max_length=128)


class UserLogin(UserBase):
    password: str = Field(min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(UserBase):
    id: int
    nickname: str
    is_active: bool
    is_admin: bool
    is_email_confirmed: bool
    is_verified_account: bool
    is_banned: bool
    auth_provider: str
    first_name: str | None = None
    last_name: str | None = None
    bank_account: str | None = None
    billing_address: str | None = None
    pesel: str | None = None
    kyc_submitted_at: datetime | None = None
    kyc_verified_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


class VerificationCodePayload(UserBase):
    code: str = Field(min_length=1, max_length=32)


class ResendVerificationPayload(UserBase):
    pass


class KycPayload(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    bank_account: str = Field(min_length=8, max_length=34)
    billing_address: str = Field(min_length=5, max_length=255)
    pesel: str | None = Field(default=None, max_length=20)


class RegistrationResponse(BaseModel):
    message: str
