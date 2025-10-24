from pydantic import BaseModel, constr


class LoginRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=3)
    password: constr(min_length=8)