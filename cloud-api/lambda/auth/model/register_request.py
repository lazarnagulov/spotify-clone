from datetime import date

from pydantic import BaseModel, constr, EmailStr


class RegisterRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=3)
    email: EmailStr
    password: constr(min_length=8)
    name: constr(strip_whitespace=True)
    family_name: constr(strip_whitespace=True)
    birthdate: date