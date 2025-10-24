from pydantic import BaseModel, constr


class UserConfirmationRequest(BaseModel):
    username: constr(strip_whitespace=True, min_length=3)
    code: constr(strip_whitespace=True, min_length=6, max_length=6)