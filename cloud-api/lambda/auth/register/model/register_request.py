from datetime import datetime, date

from pydantic import BaseModel, constr, EmailStr, validator, field_validator

from util.logger import logger

class RegisterRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=3)
    email: EmailStr
    password: constr(min_length=8)
    name: constr(strip_whitespace=True)
    family_name: constr(strip_whitespace=True)
    birthdate: str

    @field_validator("birthdate", mode="before")
    @classmethod
    def validate_birthdate(cls, value: str) -> str:
        try:
            parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            logger.info("Failed to parse birthdate")
            raise ValueError("Birthdate must be in YYYY-MM-DD format.")

        if parsed_date > date.today():
            logger.info("Birthdate is in the future")
            raise ValueError("Birthdate cannot be in the future.")

        return value
