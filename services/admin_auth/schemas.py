from pydantic import BaseModel, EmailStr, Field, ConfigDict


class AdminBase(BaseModel):
    email: EmailStr


class AdminCreate(AdminBase):
    password: str = Field(min_length=8, max_length=128)


class AdminLogin(AdminBase):
    password: str = Field(min_length=1)

class ResetCodePayload(AdminBase):
    pass

class ConfirmCodePayload(AdminBase):
    code: str = Field(min_length=1, max_length=32)

class NewPasswordPayload(AdminBase):
    code: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    confirmPassword: str = Field(min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminRead(AdminBase):
    id: int
    is_active: bool
    is_admin: bool
    auth_provider: str
    model_config = ConfigDict(from_attributes=True)


class ModerationPayload(BaseModel):
    user_id: int = Field(gt=0)
